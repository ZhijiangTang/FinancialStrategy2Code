package server

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"path/filepath"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"github.com/sirupsen/logrus"
)

// 读写安全保护 应该为每一个conn都维护一个mutex

func safeWrite(conn *websocket.Conn, msg map[string]interface{}, mu *sync.RWMutex) error {
	mu.Lock()
	defer mu.Unlock()
	return conn.WriteJSON(msg)
}

func handlerNotice(conn *websocket.Conn, sessionID, chatID, message string, mu *sync.RWMutex) {
	// 发送通知
	notice := map[string]interface{}{
		"type":      "notice",
		"sessionID": sessionID,
		"chatID":    chatID,
		"message":   message,
	}
	if err := safeWrite(conn, notice, mu); err != nil {
		logrus.Error("发送通知失败:", err)
	}
}
func readFiles(conn *websocket.Conn, chatID string, mu *sync.RWMutex) {
	// chatID 作为目录名
	dirPath := chatID
	dirPath = "agentfiles"
	// 获取文件信息
	if filesList, err := getFilesInfo(dirPath); err == nil {
		for idx, file := range filesList {
			//time.Sleep(1 * time.Second)
			time.Sleep(500 * time.Millisecond)
			file["chatID"] = chatID
			file["index"] = idx
			file["fileSum"] = len(filesList)
			if err := safeWrite(conn, file, mu); err != nil {
				logrus.Error("Forward error:", err)
			}
		}
	} else {
		logrus.Errorf("获取文件信息失败: %v", err)
	}
}
func saveFileData(conn *websocket.Conn, msg map[string]interface{}, sessionID, chatID string, mu *sync.RWMutex) string {
	// 提取文件数据
	fileName, ok := msg["fileName"].(string)
	if !ok || fileName == "" {
		WebsocketError(conn, "无效的文件名")
		return ""
	}

	fileOriginName, ok := msg["fileOriginName"].(string)
	if !ok || fileOriginName == "" {
		WebsocketError(conn, "无效的文件名")
		return ""
	}
	fileExtension, ok := msg["fileExtension"].(string)
	if !ok || fileExtension == "" {
		WebsocketError(conn, "无效的文件后缀名")
		return ""
	}

	fileDataBase64, ok := msg["fileData"].(string)
	if !ok || fileDataBase64 == "" {
		WebsocketError(conn, "无效的文件数据")
		return ""
	}

	// 解码Base64
	fileData, err := base64.StdEncoding.DecodeString(fileDataBase64)
	if err != nil {
		logrus.Errorf("Base64解码失败: %v", err)
		WebsocketError(conn, "文件解码失败")
		return ""
	}

	// 保存文件
	if err := saveFile(fileName+"."+fileExtension, fileData); err != nil {
		logrus.Error(err)
		WebsocketError(conn, err.Error())
		return ""
	}

	// 发送成功响应
	successMsg := map[string]interface{}{
		"type":           "file_ack",
		"sessionID":      sessionID,
		"chatID":         chatID,
		"fileName":       fileName,
		"fileOriginName": fileOriginName,
		"status":         "success",
	}

	if err := safeWrite(conn, successMsg, mu); err != nil {
		logrus.Error("发送通知失败:", err)
	}
	return filepath.Join(UploadFilesDir, fileName+"."+fileExtension)
}
func handlerTextData(conn *websocket.Conn, msg map[string]interface{}, sessionID, chatID string, mu *sync.RWMutex) {
	handlerNotice(conn, sessionID, chatID, "文件处理中...", mu)
	time.Sleep(5 * time.Second)
	handlerNotice(conn, sessionID, chatID, "第一阶段...", mu)
	time.Sleep(5 * time.Second)
	// handlerNotice(conn, sessionID, chatID, "第二阶段...", mu)

	// 提取文字数据

	if text, ok := msg["text"].(string); ok {
		// 创建一个消息对象
		logrus.Debug("发送了文本数据，数据为:", text)

		// 向python的flask服务器发送agent请求
		// 请求带有text 和 chatID， chatID是一个对话的ID，专门去里面找文件
		// 向 flask 发请求 ---> 包含文字信息  等后面flask返回响应后才继续下面的逻辑
		// 创建 HTTP 客户端并设置超时
		// 准备请求数据
		requestData := map[string]string{
			"type":   "text",
			"text":   text,
			"chatID": chatID,
		}
		jsonData, err := json.Marshal(requestData)
		if err != nil {
			logrus.Errorf("JSON编码失败: %v", err)
			WebsocketError(conn, "请求格式错误")
			return
		}
		// 发送请求到 Flask 服务器
		// 使用 HTTP POST 请求会阻塞等待服务器响应
		start := time.Now() // 记录开始时间
		resp, err := httpClient.Post(fmt.Sprintf("%s/generateCode", FlaskAddr), "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			logrus.Errorf("请求Flask服务器失败: %v", err)
			WebsocketError(conn, "无法连接到处理服务")
			return
		}
		defer resp.Body.Close()
		logrus.Debugf("调用模型执行耗时: %v", time.Since(start))
		// 检查响应状态
		if resp.StatusCode != http.StatusOK {
			logrus.Errorf("Flask服务器返回错误状态: %d", resp.StatusCode)
			WebsocketError(conn, "处理服务返回错误")
			return
		}

		// 读取响应体
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			logrus.Errorf("读取响应失败: %v", err)
			WebsocketError(conn, "处理服务响应错误")
			return
		}

		// 处理响应（可选）
		logrus.Debugf("Flask服务器响应: %s", string(body))
		var responseData FlaskResponse
		if err := json.Unmarshal(body, &responseData); err != nil {
			logrus.Errorf("解析JSON响应失败: %v", err)
			WebsocketError(conn, "响应格式错误")
			return
		}
		if responseData.Status == 1 {
			logrus.Debug("正确的响应")
			readFiles(conn, chatID, mu)
		} else {
			// 失败逻辑
			logrus.Errorf("Flask 处理失败，状态码: %d, 消息: %s", responseData.Status, responseData.Message)
			WebsocketError(conn, fmt.Sprintf("处理失败: %s", responseData.Message))
		}

	} else {
		logrus.Error("没有文本数据")
	}
}

func handlerFileData(conn *websocket.Conn, msg map[string]interface{}, sessionID, chatID string, mu *sync.RWMutex) {
	// 提取文件名和文件数据

	// 然后处理文件（同handlerFileData）
	filePath := saveFileData(conn, msg, sessionID, chatID, mu)
	if filePath == "" {
		WebsocketError(conn, "文件保存失败")
		return
	}
	time.Sleep(1 * time.Second)
	// 处理文件数据（如存储或转发）
	handlerNotice(conn, sessionID, chatID, "PDF阅读中...", mu)
	time.Sleep(2 * time.Second)
	handlerNotice(conn, sessionID, chatID, "初始化API客户端并加载知识库...", mu)
	time.Sleep(3 * time.Second)
	handlerNotice(conn, sessionID, chatID, "重写查询...", mu)
	time.Sleep(1 * time.Second)
	handlerNotice(conn, sessionID, chatID, "FAISS向量检索...", mu)
	time.Sleep(2 * time.Second)
	handlerNotice(conn, sessionID, chatID, "大模型重排序...", mu)
	time.Sleep(1 * time.Second)
	handlerNotice(conn, sessionID, chatID, "生成最终答案...", mu)
	time.Sleep(4 * time.Second)
	// 向 flask 发请求 ---> 包含text和文件路径

	// 向python的flask服务器发送agent请求
	// 请求带有text 和 chatID， chatID是一个对话的ID，专门去里面找文件
	// 向 flask 发请求 ---> 包含文字信息  等后面flask返回响应后才继续下面的逻辑
	// 创建 HTTP 客户端并设置超时

	// 准备请求数据
	requestData := map[string]string{
		"type":     "file",
		"chatID":   chatID,
		"filePath": filePath,
	}
	start := time.Now() // 记录开始时间
	jsonData, err := json.Marshal(requestData)
	if err != nil {
		logrus.Errorf("JSON编码失败: %v", err)
		WebsocketError(conn, "请求格式错误")
		return
	}
	// 发送请求到 Flask 服务器
	// 使用 HTTP POST 请求会阻塞等待服务器响应
	resp, err := httpClient.Post(fmt.Sprintf("%s/generateCode", FlaskAddr), "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		logrus.Errorf("请求Flask服务器失败: %v", err)
		WebsocketError(conn, "无法连接到处理服务")
		return
	}
	defer resp.Body.Close()
	logrus.Debugf("调用模型执行耗时: %v", time.Since(start))
	// 检查响应状态
	if resp.StatusCode != http.StatusOK {
		logrus.Errorf("Flask服务器返回错误状态: %d", resp.StatusCode)
		WebsocketError(conn, "处理服务返回错误")
		return
	}

	// 读取响应体
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		logrus.Errorf("读取响应失败: %v", err)
		WebsocketError(conn, "处理服务响应错误")
		return
	}

	// 处理响应（可选）
	logrus.Debugf("Flask服务器响应: %s", string(body))

	readFiles(conn, chatID, mu)
}

func handlerFileTextData(conn *websocket.Conn, msg map[string]interface{}, sessionID, chatID string, mu *sync.RWMutex) {
	handlerNotice(conn, sessionID, chatID, "文件处理中...", mu)
	// 处理文字数据和文件
	// 先处理文本
	text, ok := msg["text"].(string)
	if !ok && text == "" {
		logrus.Error("没有文本数据")
		WebsocketError(conn, "处理服务返回错误")
		return
	}

	// 然后处理文件（同handlerFileData）
	filePath := saveFileData(conn, msg, sessionID, chatID, mu)
	if filePath == "" {
		WebsocketError(conn, "文件保存失败")
		return
	}
	// 向 flask 发请求 ---> 包含text和文件路径

	// 向python的flask服务器发送agent请求
	// 请求带有text 和 chatID， chatID是一个对话的ID，专门去里面找文件
	// 向 flask 发请求 ---> 包含文字信息  等后面flask返回响应后才继续下面的逻辑
	// 创建 HTTP 客户端并设置超时

	// 准备请求数据
	requestData := map[string]string{
		"type":     "all",
		"text":     text,
		"chatID":   chatID,
		"filePath": filePath,
	}
	start := time.Now() // 记录开始时间
	jsonData, err := json.Marshal(requestData)
	if err != nil {
		logrus.Errorf("JSON编码失败: %v", err)
		WebsocketError(conn, "请求格式错误")
		return
	}
	// 发送请求到 Flask 服务器
	// 使用 HTTP POST 请求会阻塞等待服务器响应
	resp, err := httpClient.Post(fmt.Sprintf("%s/generateCode", FlaskAddr), "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		logrus.Errorf("请求Flask服务器失败: %v", err)
		WebsocketError(conn, "无法连接到处理服务")
		return
	}
	defer resp.Body.Close()
	logrus.Debugf("调用模型执行耗时: %v", time.Since(start))
	// 检查响应状态
	if resp.StatusCode != http.StatusOK {
		logrus.Errorf("Flask服务器返回错误状态: %d", resp.StatusCode)
		WebsocketError(conn, "处理服务返回错误")
		return
	}

	// 读取响应体
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		logrus.Errorf("读取响应失败: %v", err)
		WebsocketError(conn, "处理服务响应错误")
		return
	}

	// 处理响应（可选）
	logrus.Debugf("Flask服务器响应: %s", string(body))

	readFiles(conn, chatID, mu)
}

// WebSocket 连接管理
func handlerData(conn *websocket.Conn, msg map[string]interface{}, sessionID string, dataType string, mu *sync.RWMutex) {
	chatID, ok := msg["chatID"].(string)
	if !ok {
		WebsocketError(conn, "没有chatID")
		return
	}
	switch dataType {
	case "text":
		handlerTextData(conn, msg, sessionID, chatID, mu)
	case "file":
		handlerFileData(conn, msg, sessionID, chatID, mu)
	case "all":
		handlerFileTextData(conn, msg, sessionID, chatID, mu)
	default:
		logrus.Debug("unknown data type:", dataType)
		WebsocketError(conn, "unknown data type")
	}

}

// 处理设备与服务器之间断开连接
func handlerServiceDisconnect(sessionID string, mu *sync.RWMutex) {
	global_mu.Lock()
	delete(sessionConns, sessionID)
	global_mu.Unlock()
	logrus.Debug("sessionID disconnected:", sessionID)
}
