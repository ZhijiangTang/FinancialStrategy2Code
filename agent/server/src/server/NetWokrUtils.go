package server

import (
	"encoding/json"
	"errors"
	"log"
	"net"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

var mu sync.RWMutex

// error

// 这个前端要用try catch才能捕获错误
func HttpError(w http.ResponseWriter, err error, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	_ = json.NewEncoder(w).Encode(map[string]string{
		"error": err.Error(),
	})
}
func JsonError(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  0,
		"message": message,
	})
}

func GetClientIP(r *http.Request, port_if bool) (string, error) {
	if port_if {
		return r.RemoteAddr, nil
	}
	// 从 RemoteAddr 中提取 IP 地址
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		log.Println("ip 获取失败")
		return "", err
	}
	ip := net.ParseIP(host)
	if ip == nil {
		log.Println("ip 解析失败")
		return "", errors.New("无法解析 IP 地址: " + host)
	}
	return ip.String(), nil
}
func ReadJSONWithTimeout(conn *websocket.Conn, timeoutSec int) (map[string]interface{}, error) {
	// 设置读取超时
	conn.SetReadDeadline(time.Now().Add(time.Duration(timeoutSec) * time.Second))

	// 读取JSON消息
	var msg map[string]interface{}
	mu.Lock()
	defer mu.Unlock()
	err := conn.ReadJSON(&msg)
	if err != nil {
		return nil, err
	}

	// 重置超时设置（避免影响后续操作）
	conn.SetReadDeadline(time.Time{})
	return msg, nil
}

// websocket error
func WebsocketError(conn *websocket.Conn, message string) {
	_ = conn.WriteJSON(map[string]interface{}{
		"type":    "error",
		"message": message,
	})
}
