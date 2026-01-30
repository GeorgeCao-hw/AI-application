# openEuler Website Search MCP System

这是一个基于 MCP (Model Context Protocol) 的 openEuler 网站内容搜索系统，提供智能对话界面帮助用户快速查找网站内容。

## 功能特性

- 🔍 **智能搜索**: 在 openEuler 网站上搜索关键词，返回相关内容片段和链接
- 📄 **页面获取**: 获取特定页面的完整内容
- 🗺️ **网站导航**: 查看网站主要板块和结构
- 💬 **对话界面**: 自然语言交互，智能理解用户需求

## 系统架构

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│             │  MCP    │             │  HTTP   │              │
│  MCP Client │◄───────►│  MCP Server │◄───────►│  openEuler   │
│  (对话界面)  │         │  (工具提供)  │         │   Website    │
│             │         │             │         │              │
└─────────────┘         └─────────────┘         └──────────────┘
```

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置 API Key

```bash
export DEEPSEEK_API_KEY='sk-xxxxx'
```

### 2. 设置 API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## 使用方法

### 启动对话界面

```bash
python3 mcp_client.py
```

### 示例对话

```
👤 You: 如何下载 openEuler？

🤖 Assistant: 您可以访问 openEuler 的下载页面...

👤 You: 有哪些文档资源？

🤖 Assistant: openEuler 提供了全面的技术文档...
```

## MCP Server 提供的工具

### 1. search_openeuler
搜索 openEuler 网站内容
- **参数**:
  - `query`: 搜索关键词
  - `url`: 可选，指定搜索的页面 URL
- **返回**: 匹配的文本片段和相关链接

### 2. get_page_content
获取特定页面的完整内容
- **参数**:
  - `url`: 页面 URL
- **返回**: 页面标题、文本内容和所有链接

### 3. get_main_sections
获取网站主要板块
- **参数**: 无
- **返回**: 主要板块列表（下载、文档、安全中心等）

## 技术栈

- **MCP Protocol**: Anthropic 的 Model Context Protocol
- **DeepSeek API**: DeepSeek Chat 模型
- **Web Scraping**: httpx + BeautifulSoup
- **Python**: 异步编程 (asyncio)

## 主要文件说明

- `mcp_server.py`: MCP 服务器，提供网站搜索工具
- `mcp_client.py`: MCP 客户端，提供对话界面
- `requirements.txt`: Python 依赖包列表
- `README.md`: 项目文档

## 注意事项

1. 需要有效的 DeepSeek API Key
2. 需要网络连接访问 openEuler 网站
3. 首次访问页面会有缓存，后续访问更快

## 故障排除

### 问题: "DEEPSEEK_API_KEY environment variable not set"
**解决**: 设置环境变量 `export DEEPSEEK_API_KEY='your-key'`

### 问题: 连接超时
**解决**: 检查网络连接，确保可以访问 https://www.openeuler.org

### 问题: 模块导入错误
**解决**: 运行 `pip install -r requirements.txt` 安装所有依赖

## 许可证

MIT License
