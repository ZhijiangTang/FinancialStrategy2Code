import json
import os
import sys

def test_load_json():
    file_path = "/root/autodl-tmp/FinancialStrategy2Code/datasets/merged_strategy_dataset.json"
    
    # 检查路径是否存在
    print(f"Checking if path exists: {file_path}")
    if not os.path.exists(file_path):
        print(f"ERROR: File does not exist at {file_path}")
        # 列出目录内容
        parent_dir = os.path.dirname(file_path)
        if os.path.exists(parent_dir):
            print(f"\nContents of {parent_dir}:")
            for item in os.listdir(parent_dir):
                print(f"  {item}")
        else:
            print(f"Parent directory {parent_dir} does not exist")
        return False

    # 尝试读取文件
    try:
        print(f"Attempting to read file...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("Successfully loaded JSON file")
        print(f"Found {len(data)} strategies")
        return True
    except UnicodeDecodeError as e:
        print(f"Encoding error: {str(e)}")
        print("Trying with different encodings...")
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                print(f"Successfully loaded using {encoding} encoding")
                return True
            except:
                continue
        print("Failed with all encodings")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print("First 100 characters of file content:")
        with open(file_path, 'r') as f:
            print(f.read(100))
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Python version: {sys.version}")
        print(f"File info: {os.stat(file_path)}")
        return False

if __name__ == "__main__":
    test_load_json()
