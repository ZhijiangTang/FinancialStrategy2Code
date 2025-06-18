package server

import (
	"fmt"
	"os"
	"runtime"

	"github.com/sirupsen/logrus"
)

func init() {
	// 设置日志输出到标准输出
	logrus.SetOutput(os.Stdout)
	/*
		// 设置日志格式为 JSON
		logrus.SetFormatter(&logrus.JSONFormatter{
			TimestampFormat: "2006-01-02 15:04:05", // 自定义时间格式
			CallerPrettyfier: func(f *runtime.Frame) (string, string) {
				// 返回文件名和行号
				return "", fmt.Sprintf("%s:%d", f.File, f.Line)
			},
		})
	*/
	// 如果希望日志以更易读的格式输出，可以使用 logrus.TextFormatter

	logrus.SetFormatter(&logrus.TextFormatter{
		TimestampFormat: "2006-01-02 15:04:05", // 自定义时间格式
		FullTimestamp:   true,                  // 显示完整时间
		CallerPrettyfier: func(f *runtime.Frame) (string, string) {
			// 返回文件名和行号
			return "", fmt.Sprintf("%s:%d", f.File, f.Line)
		},
		ForceColors:   true,  // 强制启用颜色
		DisableColors: false, // 不禁用颜色
		PadLevelText:  true,  // 对齐日志级别
	})

	// 启用记录调用者信息（文件名和行号）
	logrus.SetReportCaller(true)

	// 设置日志级别为 Debug
	logrus.SetLevel(logrus.DebugLevel)
	logrus.AddHook(&logrusHook{})
}

type logrusHook struct{}

func (hook *logrusHook) Levels() []logrus.Level {
	return logrus.AllLevels // 适用于所有日志级别
}
func (hook *logrusHook) Fire(entry *logrus.Entry) error {
	// 在日志前后添加分割线
	fmt.Println("----------------------------------------")
	// 绿色：\x1b[32m  黄色：\x1b[33m 蓝色：\x1b[34m 紫色：\x1b[35m 青色：\x1b[36m 白色：\x1b[37m
	entry.Message = fmt.Sprintf("\x1b[31m%s\x1b[0m", entry.Message) // \x1b[31m 表示红色，\x1b[0m 表示重置颜色
	fmt.Println(entry.Message)
	fmt.Println("----------------------------------------")
	return nil
}
func test() {
	// 记录不同级别的日志
	logrus.Debug("This is a debug message")  // Debug 级别
	logrus.Info("This is an info message")   // Info 级别
	logrus.Warn("This is a warning message") // Warn 级别
	logrus.Error("This is an error message") // Error 级别

	// 记录带有字段的日志
	logrus.WithFields(logrus.Fields{
		"key1": "value1",
		"key2": "value2",
	}).Info("This is a log with fields")
}
