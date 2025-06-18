"""
CodeScore类用于评估代码生成的质量。

这个类使用OpenAI API（或兼容的API）来评估生成的代码与论文描述的匹配程度。
它支持两种评估模式：无参考评估(ref_free)和基于参考的评估(ref_based)。

主要功能：
1. 读取论文内容和生成的代码
2. 使用大语言模型进行评分（已优化为并发请求）
3. 收集多个评估结果并计算平均分数
4. 保存详细的评估结果和理由

使用示例：
    codescore = CodeScore(eval_type="ref_free")
    # 注意：现在需要使用 await
    result = asyncio.run(codescore.score(
        strategy_name="Transformer",
        pdf_json_path="./examples/Transformer_cleaned.json",
        target_repo_dir="./outputs/Transformer_repo",
        gold_repo_dir=""
    ))
"""

import json
from openai import AsyncOpenAI  # <<< MODIFIED: 导入异步客户端
import os
import sys
import asyncio  # <<< MODIFIED: 导入asyncio库

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codes.utils import read_all_files, num_tokens_from_messages, extract_json_from_string, get_now_str, print_log_cost
from tqdm import tqdm

# 设置API配置
os.environ["BASE_URL"] = "https://api.siliconflow.cn/v1"
with open("./api_key/SiliconCloud.api") as f:
    os.environ["OPENAI_API_KEY"] = f.readline()

class CodeScore():
    """
    代码评分类，用于评估生成的代码质量。

    参数:
        generated_n (int): 生成评估结果的次数，默认为5
        model (str): 使用的模型名称，默认为"Qwen/Qwen3-8B"
        eval_type (str): 评估类型，可选"ref_free"或"ref_based"，默认为"ref_based"
        eval_result_dir (str): 评估结果保存目录，默认为"score"
    """
    def __init__(self, generated_n=5, model="Qwen/Qwen3-30B-A3B", eval_type="ref_based", eval_result_dir="score") -> None:
        # <<< MODIFIED: 使用异步客户端 AsyncOpenAI
        self.client = AsyncOpenAI(base_url=os.environ["BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])
        self.eval_type = eval_type
        self.generated_n = generated_n
        self.model = model
        self.eval_result_dir = eval_result_dir

    # <<< MODIFIED: 将函数改为异步
    async def api_call(self, request_json):
        """
        调用API进行评分。

        参数:
            request_json (dict): API请求参数

        返回:
            completion: API返回的完成结果
        """
        # <<< MODIFIED: 使用 await 等待异步调用完成
        completion = await self.client.chat.completions.create(**request_json)
        return completion

    def read_strategy(self, pdf_json_path):
        """
        读取论文策略文件。

        参数:
            pdf_json_path (str): 论文JSON文件路径

        返回:
            dict: 论文内容
        """
        with open(f'{pdf_json_path}') as f:
            paper_json = json.load(f)
        return paper_json

    def read_code(self, target_repo_dir, allowed_ext=[".py", ".yaml", ".yml", ".md", ".sh", ".bash"], is_print=False):
        """
        读取代码文件。

        参数:
            target_repo_dir (str): 目标代码仓库目录
            allowed_ext (list): 允许的文件扩展名列表
            is_print (bool): 是否打印文件信息

        返回:
            str: 格式化后的代码字符串
        """
        target_files_dict = read_all_files(target_repo_dir, allowed_ext=allowed_ext, is_print=is_print)
        codes = ""
        for file_name, code in target_files_dict.items():
            codes += f"```## File name: {file_name}\n{code}\n```\n\n"
        return codes
    
    # <<< MODIFIED: 将主评分函数改为异步
    async def score(self, strategy_name,
                    paper_json=None, codes=None, goldcodes=None,
                    pdf_json_path=None, target_repo_dir=None, gold_repo_dir=None):
        """
        执行代码评分。

        参数:
            strategy_name (str): 策略名称
            paper_json (dict, optional): 论文内容
            codes (str, optional): 生成的代码
            goldcodes (str, optional): 参考代码
            pdf_json_path (str, optional): 论文JSON文件路径
            target_repo_dir (str, optional): 目标代码仓库目录
            gold_repo_dir (str, optional): 参考代码仓库目录

        返回:
            dict: 评估结果，包含分数和评估理由
        """
        prompt = open(f"./prompts/score/{self.eval_type}.txt").read()

        if paper_json is None:
            paper_json = self.read_strategy(pdf_json_path)
        if codes is None:
            codes = self.read_code(target_repo_dir)
        cur_prompt = prompt.replace('{{Paper}}', f"{paper_json}").replace('{{Code}}', codes)
        if self.eval_type == "ref_based":
            if goldcodes is None:
                goldcodes = self.read_code(gold_repo_dir)
            cur_prompt = cur_prompt.replace('{{GoldCode}}', f"{goldcodes}")
        msg = [{"role": "system", "content": cur_prompt}]

        try:
            num_tokens = num_tokens_from_messages(msg)
        except Exception as e:
            print(f"[WARNING] An exception was raised while counting tokens for the target repository of {strategy_name}.")
            print(e)
            print("-" * 40)
            num_tokens = 0
        assert num_tokens <= 128000

        score_key = "score"
        rationale_key = "critique_list"

        all_scores = []
        rationales = []
        
        # <<< MODIFIED: 并发执行API调用
        request_json = {
            "model": self.model,
            "messages": msg,
            "temperature": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        }

        # 创建一个包含所有API调用任务的列表
        tasks = [self.api_call(request_json) for _ in range(self.generated_n)]
        
        print(f"Sending {self.generated_n} requests concurrently...")
        # 使用 asyncio.gather 并发运行所有任务
        completions = await asyncio.gather(*tasks, return_exceptions=True)
        print("All responses received.")

        last_completion_json = None # 用于日志记录
        
        # 处理所有返回的结果
        for completion in completions:
            if isinstance(completion, Exception):
                print(f"[WARNING] An API call failed with an exception: {completion}")
                continue

            completion_json = json.loads(completion.model_dump_json())
            last_completion_json = completion_json # 保存最后一个用于日志
            choice = completion_json['choices'][0]
            output = choice['message']['content'].strip()

            try:
                output_json2 = json.loads(output)
                score = int(output_json2[score_key])
                rationale = json.dumps(output_json2.get(rationale_key, ""))
            except (json.JSONDecodeError, KeyError, TypeError):
                try:
                    output_json2 = json.loads(extract_json_from_string(output))
                    score = int(output_json2[score_key])
                    rationale = json.dumps(output_json2.get(rationale_key, ""))
                except Exception as e2:
                    print(f"[WARNING] Invalid response: parsing error. Details: {e2}")
                    print("-" * 40)
                    continue

            if not 1 <= score <= 5:
                print(f"[WARNING] Invalid score: {score}. Score must be between 1 and 5.")
                continue

            all_scores.append(score)
            rationales.append(rationale)

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

        output_json = {
            "strategy_name": strategy_name,
            "target_repo_dir": target_repo_dir,
            "eval_type": self.eval_type,
            "gold_repo_dir": gold_repo_dir,
            "generated_n": self.generated_n,
            "request_json": request_json, # Note: this is the template, not individual requests
            "completion_json": last_completion_json, # For logging purposes
            "eval_result": {
                "score": avg_score,
                "valid_n": len(all_scores),
                "score_lst": all_scores,
                "rationale_lst": rationales,
            },
        }

        now_str = get_now_str()
        output_dir = os.path.join(self.eval_result_dir, f"{strategy_name}_eval_{self.eval_type}_{self.model.replace('/', '_')}_{now_str}")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "score.json"), 'w', encoding='utf-8') as f:
            json.dump(output_json, f, indent=4) # Use indent for readability

        print()
        print("=" * 40)
        print("🌟 Evaluation Summary 🌟")
        print(f"📄 Strategy name: {strategy_name}")
        print(f"⚖️ Evaluation type: {self.eval_type}")
        print(f"📁 Target repo directory: {target_repo_dir}")
        print(f"📊 Evaluation result:")
        print(f"\t📈 Score: {avg_score:.4f}")
        print(f"\t✅ Valid responses: {output_json['eval_result']['valid_n']}/{self.generated_n}")
        print("=" * 40)

        if last_completion_json:
            print_log_cost(last_completion_json, self.model, f"[Evaluation] {strategy_name} - {self.eval_type}", output_dir, 0)
        
        return output_json

# <<< MODIFIED: 更新主执行块以使用asyncio
async def main():
    # 使用示例
    codescore = CodeScore(eval_type="ref_based")
    paper = ""
    answer = ""
    try:
        with open("/home/sonata/FinancialStrategy2Code/strategies/海龟.txt", 'r', encoding='utf-8') as f:
            paper = f.read()
    except FileNotFoundError:
        print("Error: Strategy file not found. Please check the path.")
        return
    
    try:
        with open("/home/sonata/FinancialStrategy2Code/strategies/海龟答案.txt", 'r', encoding='utf-8') as f:
            answer = f.read()
    except FileNotFoundError:
        print("Error: Strategy file not found. Please check the path.")
        return

    # 使用 await 调用异步的 score 方法
    await codescore.score(
        strategy_name="海龟交易",
        paper_json=paper,
        target_repo_dir="/home/sonata/FinancialStrategy2Code/outputs/海龟_repo",
        gold_repo_dir=answer
    )
    print("end")

if __name__ == "__main__":
    # 运行主异步函数
    asyncio.run(main())