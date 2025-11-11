#!/bin/bash

# 一键启动脚本
set -e

echo "=========================================="
echo "启动 LangGraph Plan-and-React Agent"
echo "=========================================="

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "警告: .env 文件不存在，请先创建并配置环境变量"
    echo ""
    echo "必需的环境变量："
    echo "  - AZURE_OPENAI_API_KEY: Azure OpenAI API 密钥"
    echo "  - AZURE_OPENAI_ENDPOINT: Azure OpenAI 端点 URL"
    echo "  - AZURE_OPENAI_DEPLOYMENT_NAME: Azure OpenAI 部署名称（可选，默认使用模型名）"
    echo ""
    echo "可选的环境变量："
    echo "  - AZURE_OPENAI_API_VERSION: API 版本（默认: 2024-02-15-preview）"
    echo "  - AZURE_OPENAI_DEPLOYMENT_NAME_PLANNER: Planner 使用的部署名称"
    echo "  - AZURE_OPENAI_DEPLOYMENT_NAME_EXECUTOR: Executor 使用的部署名称"
    echo "  - AZURE_OPENAI_DEPLOYMENT_NAME_REPLANNER: Replanner 使用的部署名称"
    echo "  - TAVILY_API_KEY: Tavily 搜索 API 密钥（用于搜索功能）"
    echo ""
    read -p "是否继续启动? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查 docker compose 是否可用
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到 docker 命令，请先安装 Docker"
    exit 1
fi

# 构建并启动容器
echo "正在构建 Docker 镜像..."
docker compose build

echo "正在启动容器..."
docker compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查容器状态
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "=========================================="
    echo "✅ 服务启动成功！"
    echo "=========================================="
    echo ""
    echo "访问地址: http://localhost:8123"
    echo ""
    echo "查看日志: docker compose logs -f"
    echo "停止服务: ./stop.sh"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ 服务启动失败，请查看日志:"
    echo "=========================================="
    docker compose logs
    exit 1
fi

