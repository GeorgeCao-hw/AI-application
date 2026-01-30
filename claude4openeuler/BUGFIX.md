# 错误修复说明

## 问题描述

运行 `mcp_client.py` 时出现错误：
```
TypeError: object _AsyncGeneratorContextManager can't be used in 'await' expression
```

## 根本原因

`stdio_client()` 返回的是一个异步上下文管理器（async context manager），需要使用 `async with` 语法，而不是 `await`。

## 解决方案

### 修改前的代码
```python
async def connect_to_server(self):
    stdio_transport = await stdio_client(server_params)  # ❌ 错误
    self.stdio, self.write = stdio_transport
    self.session = ClientSession(self.stdio, self.write)
    await self.session.__aenter__()
```

### 修改后的代码
```python
async def __aenter__(self):
    """Async context manager entry"""
    # Use async context manager for stdio_client
    self.stdio_context = stdio_client(server_params)
    stdio_transport = await self.stdio_context.__aenter__()  # ✅ 正确
    read_stream, write_stream = stdio_transport

    # Create session
    self.session = ClientSession(read_stream, write_stream)
    self.session_context = self.session
    await self.session_context.__aenter__()

    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Async context manager exit"""
    if self.session_context:
        await self.session_context.__aexit__(exc_type, exc_val, exc_tb)
    if self.stdio_context:
        await self.stdio_context.__aexit__(exc_type, exc_val, exc_tb)
```

### 使用方式更新
```python
# 修改前
client = OpenEulerChatClient(api_key)
await client.connect_to_server()
await client.interactive_chat()
await client.close()

# 修改后
async with OpenEulerChatClient(api_key) as client:  # ✅ 使用 async with
    await client.interactive_chat()
```

## 验证

运行测试脚本验证修复：
```bash
python3 test_mcp_connection.py
```

预期输出：
```
✓ Successfully connected to MCP server
✓ Found 3 tools:
  - search_openeuler: ...
  - get_page_content: ...
  - get_main_sections: ...
```

## 现在可以正常使用

```bash
# 设置 API key
export DEEPSEEK_API_KEY='sk-xxxxx'

# 运行客户端
python3 mcp_client.py
```

系统现在应该可以正常启动并连接到 MCP 服务器了！
