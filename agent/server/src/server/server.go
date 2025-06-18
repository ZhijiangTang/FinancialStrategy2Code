package server

import (
	"embed"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
	"github.com/sirupsen/logrus"
)

var (
	// 16GB=16*1024*1024*1024  最多16*512个conn连接 --->要做内存优化（如果要高并发的话，那么内存优化是必须的）
	upgrader = websocket.Upgrader{
		ReadBufferSize:  10 * 1024 * 1024, //10MB 是用来接收附加数据的
		WriteBufferSize: 10 * 1024 * 1024,
		CheckOrigin:     func(r *http.Request) bool { return true }, // 允许跨域
	}
	sessionConns      = make(map[string]*SessionConn)
	global_mu         sync.RWMutex
	GeneratedFilesDir string
	UploadFilesDir    string
	FlaskAddr         string
	httpClient        = &http.Client{
		Timeout: 300 * time.Second, // 强烈建议设置超时
		Transport: &http.Transport{
			MaxIdleConns:       100,
			IdleConnTimeout:    90 * time.Second,
			DisableCompression: true,
		},
	}
)

func enableCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")              // 允许的域名
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS") // 允许的 HTTP 方法
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")  // 允许的请求头
		w.Header().Set("Access-Control-Allow-Credentials", "true")      // 允许携带凭证
		// 处理 OPTIONS 预检请求
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func healthConnect(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if r.Method == "GET" {
		HttpError(w, errors.New("Method Not Allowed"), http.StatusMethodNotAllowed)
		return
	}
	// 如果后端使用 r.Form，前端需要发送 application/x-www-form-urlencoded 格式的数据
	var jsonData = healthHandlerJSON{}
	if err := json.NewDecoder(r.Body).Decode(&jsonData); err != nil {
		logrus.Error("Failed to decode JSON:", err)
		JsonError(w, "JSON data struct has problems")
		return
	}
	localSessionID := jsonData.LocalSessionID
	targetSessionID := jsonData.TargetSessionID
	_, exist := sessionConns[targetSessionID]
	if exist {
		//询问对方设备是否接受请求？connectRequest
		targetConn := sessionConns[targetSessionID]
		askRequest := map[string]interface{}{
			"type":             "connectRequest",
			"requestSessionID": localSessionID,
			"receiveSessionID": targetSessionID,
		}
		if err := targetConn.Conn.WriteJSON(askRequest); err != nil {
			logrus.Error("Failed to send ask request:", err)
			HttpError(w, err, http.StatusInternalServerError)
			return
		}
		_ = json.NewEncoder(w).Encode(map[string]interface{}{
			"status": 1,
		})
	} else {
		logrus.Debug("health targetSessionID assert failed or empty")
		_ = json.NewEncoder(w).Encode(map[string]interface{}{
			"status":  0,
			"message": fmt.Sprint(targetSessionID, "设备离线"),
		})
		return
	}
	// 还要做回收
}

// 这个函数可以做一下封装，比如加个控制器（）
func wsHandler(w http.ResponseWriter, r *http.Request) {
	// 检查是否有重名！！即同一sessionid多次连接
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		logrus.Error("WebSocket upgrade failed:", err)
		// 这个不知道能不能处理
		WebsocketError(conn, fmt.Sprintln("WebSocket upgrade failed", err.Error()))
		return
	}
	defer conn.Close()
	//var deviceType, sessionID string
	msg, err := ReadJSONWithTimeout(conn, 5)
	if err != nil {
		logrus.Error("Failed to read message:", err)
		WebsocketError(conn, fmt.Sprintln("Failed to read message:", err.Error()))
		return
	}
	sessionID, ok := msg["sessionID"].(string)
	if !ok || sessionID == "" {
		logrus.Debug("session assert failed or empty")
		WebsocketError(conn, "session assert failed or empty")
		return
	}
	_, exist := sessionConns[sessionID]
	if exist {
		err := fmt.Sprintln("sessionID 重名: ", sessionID)
		logrus.Error(err)
		WebsocketError(conn, err)
		conn.Close()
		return
	}
	global_mu.Lock()
	local_SessionConn := &SessionConn{Conn: conn, ID: sessionID}
	sessionConns[sessionID] = local_SessionConn
	// 只要设备在连接池那么就可以实时通信
	global_mu.Unlock()
	logrus.Debug("sessionID connect  ", sessionID)

	for {
		// 使用 NextReader() 检查下一个消息
		// 不能对conn读/写数据加写锁（没有数据传入的时候，会占用锁，从而导致死锁），这样的话会导致死锁
		//local_SessionConn.mu.Lock()
		_, reader, err := conn.NextReader()
		//local_SessionConn.mu.Unlock()
		if err != nil {

			if websocket.IsCloseError(err, websocket.CloseNormalClosure, websocket.CloseGoingAway) || err == io.EOF {
				// 获取关闭帧的状态码和消息  断言websocket.CloseError的指针(即*websocket.CloseError)
				if closeErr, ok := err.(*websocket.CloseError); ok {
					statusCode := closeErr.Code
					message := closeErr.Text
					logrus.Info("WebSocket closed with code %d and message: %s", statusCode, message)
				}
				handlerServiceDisconnect(sessionID, &local_SessionConn.mu)
				break
			}
			//通用处理所有关闭错误
			/*
							WebSocket 关闭状态码：
				正常关闭：前端调用 WebSocket.close() 时，通常会发送一个关闭帧，包含状态码 1000（正常关闭）或其他标准状态码。
				异常关闭：如果前端直接关闭浏览器标签或刷新页面，可能会发送状态码 1001（离开）或 1006（异常关闭）。
				无状态码关闭：在某些情况下，前端可能未发送标准状态码，而是直接关闭连接（如状态码 1005，表示无状态码关闭）。
								websocket.IsUnexpectedCloseError(err, websocket.CloseNormalClosure, websocket.CloseGoingAway) || err == io.EOF
			*/
			// 其他错误继续下一次循环
			logrus.Error("Failed to read message:", err)
			continue
		}

		// 从 reader 中读取消息内容
		var msg map[string]interface{}
		decoder := json.NewDecoder(reader)
		if err := decoder.Decode(&msg); err != nil {
			logrus.Error("Failed to decode message:", err)
			continue
		}
		type_string, ok := msg["type"].(string)
		if !ok {
			logrus.Debug("targetSessionID assert failed or empty")
			WebsocketError(conn, "targetSessionID assert failed or empty")
			continue
		}
		if type_string == "file" || type_string == "text" || type_string == "all" {
			handlerData(conn, msg, sessionID, type_string, &local_SessionConn.mu)
		} else {
			logrus.Debug("type assert failed or empty")
			WebsocketError(conn, "type assert failed or empty")
			continue
		}
	}
}

//go:embed dist/*
var frontend embed.FS

func StartServer(generatedFilesDir, uploadFilesDir, flaskAddr string) {
	GeneratedFilesDir = generatedFilesDir
	UploadFilesDir = uploadFilesDir
	FlaskAddr = flaskAddr

	//加载静态资源
	// 创建子文件系统
	// 不允许跨模块或访问父目录（安全限制）
	distFS, _ := fs.Sub(frontend, "dist")
	// 验证嵌入文件列表（调试用）
	files, _ := fs.Glob(distFS, "*")
	logrus.Debug("嵌入的静态文件列表：", files)
	filesChild, _ := fs.Glob(distFS, "**/*")
	logrus.Debug("嵌入的子目录下的静态文件：", filesChild)
	r := mux.NewRouter()

	r.Handle("/connect", enableCORS(http.HandlerFunc(healthConnect))) // 连接验证接口
	r.Handle("/ws", enableCORS(http.HandlerFunc(wsHandler)))          // WebSocket 通信接口

	staticHandler := http.FileServer(http.FS(distFS))
	r.PathPrefix("/").Handler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		logrus.Info("Handling request for:", r.URL.Path)
		w.Header().Set("Cache-Control", "max-age=86400") //缓存一天
		staticHandler.ServeHTTP(w, r)
	}))

	http.Handle("/", r)
	// 启动服务器
	address := fmt.Sprint("0.0.0.0:8080")
	logrus.Info("Server is running on ", address)
	log.Fatal(http.ListenAndServe(address, nil))
}
