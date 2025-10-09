#!/bin/bash

# 知识库搜索系统Docker镜像构建脚本

echo "🚀 开始构建知识库搜索系统Docker镜像..."

# 构建镜像
docker build -t knowledge-search-app:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker镜像构建成功！"
    echo ""
    echo "📋 可用命令："
    echo "   1. 运行容器: docker run -p 8501:8501 knowledge-search-app:latest"
    echo "   2. 使用Docker Compose: docker-compose up"
    echo "   3. 后台运行: docker-compose up -d"
    echo ""
    echo "🌐 访问地址: http://localhost:8501"
else
    echo "❌ Docker镜像构建失败！"
    exit 1
fi