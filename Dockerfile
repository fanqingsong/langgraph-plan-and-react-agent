# 使用国内镜像加速
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 包管理器
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# 复制项目文件
COPY pyproject.toml langgraph.json ./
COPY src/ ./src/
COPY static/ ./static/ 2>/dev/null || true

# 安装项目依赖
RUN uv pip install --system -e .

# 安装 langgraph-cli
RUN uv pip install --system "langgraph-cli[inmem]>=0.2.8"

# 暴露端口（LangGraph Studio 默认端口）
EXPOSE 8123

# 启动命令
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8123"]

