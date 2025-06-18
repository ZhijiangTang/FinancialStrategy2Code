package server

import (
	"sync"

	"github.com/gorilla/websocket"
)

type Message struct {
	Action    string      `json:"action"`    // 操作类型（如 "chat", "status"）
	Data      interface{} `json:"data"`      // 动态内容（字符串、对象等）
	Error     string      `json:"error"`     // 错误信息（可选）
	Timestamp int64       `json:"timestamp"` // 时间戳
}
type SessionConn struct {
	Conn *websocket.Conn
	mu   sync.RWMutex
	ID   string
}
type healthHandlerJSON struct {
	TargetSessionID string `json:"targetSessionID"`
	LocalSessionID  string `json:"localSessionID"`
}
type wsConnectJSON struct {
	SessionID string `json:"sessionID"`
	Type      string `json:"type"`
}

type FlaskResponse struct {
	Status  int    `json:"status"`
	Message string `json:"message"`
}
