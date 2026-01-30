# 快速开始指南

## 1. 获取 DeepSeek API Key

访问 [DeepSeek Platform](https://platform.deepseek.com/) 注册并获取 API Key。

## 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 设置环境变量

```bash
export DEEPSEEK_API_KEY='sk-xxxxx'
```

## 4. 测试 API 连接

```bash
python3 test_deepseek.py
```

如果看到 "✓ DeepSeek API is working correctly!"，说明配置成功。

## 5. 启动系统

```bash
# 方式 1: 使用启动脚本
./run.sh

# 方式 2: 直接运行
python3 mcp_client.py
```

## 6. 开始对话

```
👤 You: 如何下载 openEuler？
🤖 Assistant: [AI 会使用工具搜索并回答]
```

## 常见问题

### Q: 如何获取 DeepSeek API Key?
A: 访问 https://platform.deepseek.com/ 注册账号并在控制台创建 API Key

### Q: API Key 收费吗？
A: DeepSeek 提供免费额度，具体请查看官方定价页面

### Q: 支持哪些模型？
A: 当前使用 `deepseek-chat` 模型，支持工具调用（Function Calling）

### Q: 如何退出程序？
A: 输入 `quit`、`exit` 或 `bye`，或按 Ctrl+C

## 系统要求

- Python 3.8+
- 网络连接（访问 DeepSeek API 和 openEuler 网站）
- 有效的 DeepSeek API Key

## 文件说明

- `mcp_server.py` - MCP 服务器（提供搜索工具）
- `mcp_client.py` - MCP 客户端（对话界面）
- `test_deepseek.py` - API 连接测试
- `test_server.py` - 服务器功能测试
- `run.sh` - 启动脚本
- `requirements.txt` - Python 依赖

## 下一步

查看 `EXAMPLES.md` 了解更多使用示例和高级功能。
