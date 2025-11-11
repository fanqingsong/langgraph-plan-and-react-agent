#!/bin/bash

# 一键停止脚本
set -e

echo "=========================================="
echo "停止 LangGraph Plan-and-React Agent"
echo "=========================================="

# 检查 docker compose 是否可用
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到 docker 命令"
    exit 1
fi

# 停止并删除容器
echo "正在停止容器..."
docker compose down

echo ""
echo "=========================================="
echo "✅ 服务已停止"
echo "=========================================="
echo ""
echo "如需完全清理（包括镜像），运行:"
echo "  docker compose down --rmi all"
echo ""

