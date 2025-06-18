from flask import Flask, jsonify, request
import sys
import os
import time
# 将项目根目录添加到 Python 路径，以便可以导入 model 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import load_model, predict

app = Flask(__name__)
SUCCESS = 1
ERROR = 0
# 全局变量用于存储加载的模型
model = load_model()

def handlerText(text):
    print(f"文本({text})处理中...")
    time.sleep(5)
    return True

def handlerTextAndFile(text, filePath):
    print(f"文本({text})/文件({filePath})处理中...", )
    time.sleep(5)
    return True
def handlerFile(filePath):
    print(f"文件({filePath})处理中...", )
    time.sleep(5)
    return True
@app.route('/generateCode', methods=['POST'])
def generateCode():
    if model is None:
        return jsonify({"status": ERROR, "message": "Model not loaded. Please call /load_model first."}), 400

    data = request.json
    print(data)
    type = data['type']
    try:
        if type == 'text':
            handlerText(data['text'])
            return jsonify({"status": SUCCESS, "message": "Success"})
        elif type == 'all':
            handlerTextAndFile(data['text'], data['filePath'])
            return jsonify({"status": SUCCESS, "message": "Success"})
        elif type == 'file':
            handlerFile(data['filePath'])
            return jsonify({"status": SUCCESS, "message": "Success"})
        if not data or 'input' not in data:
            return jsonify({"status": ERROR, "message": "Invalid input. Please provide 'input' in JSON body."}), 400
    except Exception as e:
        return jsonify({"status": ERROR, "message": str(e)}), 500

def App():
    print("App running...")
    app.run(debug=True, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    App()