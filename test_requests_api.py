import os
import json
import requests

def test_siliconflow_api():
    url = "https://api.siliconflow.cn/v1/chat/completions"

    headers = {
        "Authorization": os.getenv("OPENAI_API_KEY", "Bearer your_api_key_here"),
        "Content-Type": "application/json"
    }

    payload = {
        "model": os.getenv("GPT_VERSION", "Qwen/Qwen2.5-Coder-7B-Instruct"),
        "messages": [
            {"role": "user", "content": "你好，请输出'hello world'"}
        ],
        "stream": False,
        "max_tokens": 512
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)

if __name__ == "__main__":
    test_siliconflow_api()