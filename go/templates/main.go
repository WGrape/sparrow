package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/joho/godotenv"
)

func main() {
	// 加载环境变量
	err := godotenv.Load("../.env") // 注意修改路径以适应你的实际文件结构
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	// 获取环境变量 GO_CONTAINER_PORT，如果不存在则使用默认值 ":8001"
	port := os.Getenv("GO_CONTAINER_PORT")
	if port == "" {
		port = ":8001"
	}

	http.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello Go!")
	})

	// 启动 HTTP 服务器，监听端口
	fmt.Printf("Server is running on port %s\n", port)
	err = http.ListenAndServe(port, nil)
	if err != nil {
		log.Fatal("Error:", err)
	}
}
