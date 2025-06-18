package server

import (
	// 添加必要的包
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/sirupsen/logrus" // 确保已导入
)

func getFilesInfo(dirPath string) ([]map[string]interface{}, error) {
	// 1. 拼接完整路径
	fullPath := filepath.Join(GeneratedFilesDir, dirPath) // 替换base_directory为实际基础路径
	logrus.Debug("完整路径:", fullPath)
	// 2. 检查路径是否存在
	fileInfo, err := os.Stat(fullPath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, errors.New("路径不存在")
		}
		return nil, err
	}

	// 3. 确保是目录
	if !fileInfo.IsDir() {
		return nil, errors.New("路径不是目录")
	}

	// 4. 读取目录内容
	entries, err := os.ReadDir(fullPath)
	if err != nil {
		return nil, err
	}

	files := make([]fs.FileInfo, len(entries))
	for i, entry := range entries {
		files[i], err = entry.Info()
		if err != nil {
			return nil, err
		}
	}

	// 5. 收集文件信息
	// result := make(map[string]interface{})
	fileCount := 0
	fileInfos := []map[string]interface{}{}

	for _, file := range files {
		if file.IsDir() {
			continue // 跳过子目录
		}

		fileCount++

		// 获取文件后缀
		ext := filepath.Ext(file.Name())
		if ext != "" {
			ext = strings.ToLower(ext[1:]) // 去掉点并转为小写
		}

		// 读取文件内容（小文件适用）
		content, err := os.ReadFile(filepath.Join(fullPath, file.Name()))
		if err != nil {
			logrus.Warnf("读取文件 %s 失败: %v", file.Name(), err)
			content = []byte{} // 返回空内容
		}

		fileInfos = append(fileInfos, map[string]interface{}{
			"type":      "data",
			"name":      file.Name(),
			"size":      file.Size(),
			"mod_time":  file.ModTime().Format(time.RFC3339),
			"extension": ext,
			"content":   string(content),
		})
	}

	// 6. 返回结构化结果
	// result["path"] = fullPath
	// result["file_count"] = fileCount
	// result["files"] = fileInfos
	return fileInfos, nil
}

// 在 handlerFileTextData 和 handlerFileData 中添加文件处理逻辑
func saveFile(fileName string, fileData []byte) error {
	// 确保目录存在
	uploadDir := UploadFilesDir
	// 保存文件
	filePath := filepath.Join(uploadDir, fileName)
	if err := os.WriteFile(filePath, fileData, 0644); err != nil {
		return fmt.Errorf("保存文件失败: %v", err)
	}

	logrus.Infof("文件保存成功: %s (大小: %d bytes)", filePath, len(fileData))
	return nil
}
