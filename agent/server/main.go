package main

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"server"
	"strings"
)

func main() {
	osType := runtime.GOOS
	fmt.Println("当前系统为：" + osType + "\x1b")
	var inputDir, uploadDir string
	for {
		fmt.Print("\x1b[34m请输入生成的文件所在根目录:\x1b[0m")
		// fmt.Scanln(&inputDir)
		fmt.Print("\x1b[34m请输入保存文件所在根目录:\x1b[0m")
		// fmt.Scanln(&uploadDir)
		inputDir = "D:/Codes/agent/generatedFiles" // 测试用
		uploadDir = "D:/Codes/agent/uploadFiles"
		// 检查是否为空
		if inputDir == "" {
			fmt.Println("\x1b[31m错误：目录不能为空，请重新输入\x1b[0m")
			continue
		}

		// 规范化路径
		cleanPath := filepath.Clean(inputDir)
		cleanOutputPath := filepath.Clean(uploadDir)
		// 路径格式验证
		if osType == "windows" {
			// 允许盘符后的冒号（如 "C:\" 中的冒号），但禁止其他位置的冒号
			if len(cleanPath) >= 2 && cleanPath[1] == ':' {
				// 检查盘符后的路径部分是否包含非法字符
				pathWithoutDrive := cleanPath[2:]
				if strings.ContainsAny(pathWithoutDrive, `<>"|?*`) {
					fmt.Printf("\x1b[31m错误：路径包含非法字符 %s\x1b[0m\n", `<>"|?*`)
					continue
				}
			} else {
				// 对于网络路径（如 "\\server\share"），检查所有字符
				if strings.ContainsAny(cleanPath, `<>:"|?*`) {
					fmt.Printf("\x1b[31m错误：路径包含非法字符 %s\x1b[0m\n", `<>:"|?*`)
					continue
				}
			}

			if len(cleanOutputPath) >= 2 && cleanOutputPath[1] == ':' {
				// 检查盘符后的路径部分是否包含非法字符
				pathWithoutDrive := cleanOutputPath[2:]
				if strings.ContainsAny(pathWithoutDrive, `<>"|?*`) {
					fmt.Printf("\x1b[31m错误：路径包含非法字符 %s\x1b[0m\n", `<>"|?*`)
					continue
				}
			} else {
				// 对于网络路径（如 "\\server\share"），检查所有字符
				if strings.ContainsAny(cleanOutputPath, `<>:"|?*`) {
					fmt.Printf("\x1b[31m错误：路径包含非法字符 %s\x1b[0m\n", `<>:"|?*`)
					continue
				}
			}
		} else {
			// Linux/macOS路径格式: 以/开头
			// 非Windows系统：检查所有非法字符
			if strings.ContainsAny(cleanPath, `<>:"|?*`) {
				fmt.Printf("\x1b[31m错误：路径包含非法字符 %s\x1b[0m\n", `<>:"|?*`)
				continue
			}
			if strings.ContainsAny(cleanOutputPath, `<>:"|?*`) {
				fmt.Printf("\x1b[31m错误：路径包含非法字符 %s\x1b[0m\n", `<>:"|?*`)
				continue
			}
		}

		// 检查目录是否存在
		if _, err := os.Stat(cleanPath); os.IsNotExist(err) {
			fmt.Printf("\x1b[31m目录(%s)不存在 \x1b[0m\n", cleanPath)
			continue
		}

		if _, err := os.Stat(cleanOutputPath); os.IsNotExist(err) {
			fmt.Printf("\x1b[31m目录(%s)不存在 \x1b[0m\n", cleanOutputPath)
			continue
		}

		// 验证路径是目录
		if info, err := os.Stat(cleanPath); err == nil {
			if !info.IsDir() {
				fmt.Printf("\x1b[31m错误：路径(%s)不是目录\x1b[0m\n", cleanPath)
				continue
			}
		} else {
			fmt.Printf("\x1b[31m访问路径失败: %v\x1b[0m\n", err)
			continue
		}

		// 验证路径是目录
		if info, err := os.Stat(cleanOutputPath); err == nil {
			if !info.IsDir() {
				fmt.Printf("\x1b[31m错误：路径(%s)不是目录\x1b[0m\n", cleanOutputPath)
				continue
			}
		} else {
			fmt.Printf("\x1b[31m访问路径失败: %v\x1b[0m\n", err)
			continue
		}
		// 所有检查通过
		break
	}
	server.StartServer(inputDir, uploadDir, "http://127.0.0.1:5000")
}
