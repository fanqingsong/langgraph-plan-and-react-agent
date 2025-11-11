# Azure OpenAI 配置指南

本项目已配置为使用 Azure OpenAI 服务。以下是配置步骤。

## 必需的环境变量

在 `.env` 文件中配置以下环境变量：

```env
# Azure OpenAI 必需配置
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure OpenAI API 版本（可选，默认: 2024-02-15-preview）
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 可选的环境变量

如果需要为不同的组件使用不同的部署，可以配置：

```env
# 为不同组件配置不同的部署名称
AZURE_OPENAI_DEPLOYMENT_NAME_PLANNER=gpt-4-planner
AZURE_OPENAI_DEPLOYMENT_NAME_EXECUTOR=gpt-4-executor
AZURE_OPENAI_DEPLOYMENT_NAME_REPLANNER=gpt-4-replanner
```

## 其他环境变量

```env
# Tavily API Key (用于搜索功能)
TAVILY_API_KEY=tvly-your-tavily-api-key-here

# LangSmith API Key (可选，用于追踪)
LANGSMITH_API_KEY=lsv2-your-langsmith-api-key-here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=plan-and-execute
```

## 获取 Azure OpenAI 配置信息

1. **API Key**: 在 Azure Portal 中，进入你的 Azure OpenAI 资源，在"密钥和终结点"页面可以找到 API 密钥。

2. **Endpoint**: 同样在"密钥和终结点"页面，可以找到终结点 URL，格式通常为：
   ```
   https://your-resource-name.openai.azure.com/
   ```

3. **Deployment Name**: 在 Azure Portal 的"模型部署"页面，可以看到已部署的模型名称。如果没有部署，需要先创建一个部署。

4. **API Version**: 推荐使用 `2024-02-15-preview` 或更新版本。

## 示例 .env 文件

```env
# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=abc123def456...
AZURE_OPENAI_ENDPOINT=https://my-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 可选：为不同组件使用不同部署
# AZURE_OPENAI_DEPLOYMENT_NAME_PLANNER=gpt-4
# AZURE_OPENAI_DEPLOYMENT_NAME_EXECUTOR=gpt-4-turbo
# AZURE_OPENAI_DEPLOYMENT_NAME_REPLANNER=gpt-4

# Tavily 搜索 API
TAVILY_API_KEY=tvly-...

# LangSmith 追踪（可选）
LANGSMITH_API_KEY=lsv2-...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=plan-and-execute
```

## 验证配置

启动服务后，如果配置正确，服务应该能够正常启动。如果遇到错误，请检查：

1. API Key 是否正确
2. Endpoint URL 是否正确（注意末尾的斜杠）
3. Deployment Name 是否存在于你的 Azure OpenAI 资源中
4. API Version 是否支持你使用的功能

