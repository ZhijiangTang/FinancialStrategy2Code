from bs4 import BeautifulSoup
import os

def parse_financial_terms_from_html(file_path):
    """
    从本地的 Investopedia HTML 文件中解析出所有金融名词及其链接。

    Args:
        file_path (str): 本地 HTML 文件的路径。

    Returns:
        list: 一个包含字典的列表，每个字典包含 'term' 和 'url'。
              如果文件不存在则返回空列表。
    """
    if not os.path.exists(file_path):
        print(f"❌ 错误: 文件 '{file_path}' 未找到。请确保它和脚本在同一个目录下。")
        return []

    # 读取本地HTML文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    terms_list = []
    # 根据HTML结构，名词链接都在 class 为 'dictionary-top24-list__sublist' 的 <a> 标签中
    term_links = soup.find_all('a', class_='dictionary-top24-list__sublist')

    for link_tag in term_links:
        term_name = link_tag.get_text(strip=True)
        term_url = link_tag.get('href')
        if term_name and term_url:
            terms_list.append({'term': term_name, 'url': term_url})

    return terms_list

def main():
    """
    主函数，执行解析和文件写入操作。
    """
    local_html_file = 'Financial Terms Dictionary.html'
    output_file = 'financial_terms_and_links.txt'

    print(f"🚀 开始从 '{local_html_file}' 文件中解析金融名词...")
    
    # 1. 从HTML文件中解析出所有名词和链接
    terms = parse_financial_terms_from_html(local_html_file)

    if not terms:
        print("未能在HTML文件中找到任何名词。程序终止。")
        return

    print(f"✅ 成功解析到 {len(terms)} 个金融名词。")

    # 2. 将结果写入文档
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Investopedia 金融名词及链接列表\n")
        f.write("="*40 + "\n\n")
        
        for term_info in terms:
            f.write(f"名词: {term_info['term']}\n")
            f.write(f"链接: {term_info['url']}\n")
            f.write("-" * 20 + "\n")

    print(f"🎉 任务完成！所有名词和链接已保存至 '{output_file}' 文件。")
    print("\n下一步，请使用下面的第二个脚本来抓取每个链接的详细定义。")


if __name__ == '__main__':
    main()