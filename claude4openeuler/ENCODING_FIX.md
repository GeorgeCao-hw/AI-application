# 中文编码问题修复指南

## 问题描述

运行 `mcp_client.py` 后，输入中文提问时出现错误：
```
❌ Error: 'utf-8' codec can't decode byte 0xe5 in position 0: invalid continuation byte
```

## 问题分析

这个错误通常发生在以下情况：
1. **stdio 流编码不一致**: Python 进程间通信时编码设置不匹配
2. **字节流处理错误**: 将 UTF-8 字节流当作其他编码处理
3. **MCP 通信编码问题**: 客户端和服务器之间的数据传输编码不一致

## 解决方案

### 1. 添加 UTF-8 编码声明

在文件开头添加编码声明：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

### 2. 强制设置 stdio 编码

在 `mcp_server.py` 和 `mcp_client.py` 中添加：
```python
import sys

# Ensure UTF-8 encoding for stdio
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')
```

### 3. 改进工具调用错误处理

在 `process_tool_call` 方法中添加编码处理：
```python
async def process_tool_call(self, tool_name: str, tool_input: dict):
    """Execute tool call via MCP"""
    try:
        result = await self.session.call_tool(tool_name, tool_input)
        if result.content and len(result.content) > 0:
            content = result.content[0].text
            # Ensure content is properly decoded as UTF-8
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            return content
        return ""
    except Exception as e:
        error_msg = f"Tool call error: {str(e)}"
        print(f"\n⚠️  {error_msg}")
        return json.dumps({"error": error_msg}, ensure_ascii=False)
```

### 4. JSON 序列化时保留中文

确保所有 JSON 序列化都使用 `ensure_ascii=False`：
```python
json.dumps(result, indent=2, ensure_ascii=False)
```

## 验证修复

### 运行中文测试
```bash
python3 test_chinese.py
```

预期输出：
```
测试中文字符支持...
Testing Chinese character support...

测试 1: 获取主要板块
✓ 返回内容长度: 937 字符

测试 2: 使用中文搜索
搜索关键词: 下载
✓ 搜索成功，返回内容长度: 183 字符
✓ 查询: 下载
✓ 找到匹配: 0 个

✅ 所有中文测试通过！
```

## 已修改的文件

1. ✅ `mcp_server.py` - 添加 UTF-8 编码支持
2. ✅ `mcp_client.py` - 添加 UTF-8 编码支持和错误处理
3. ✅ `test_chinese.py` - 新增中文测试脚本

## 使用建议

### 启动客户端
```bash
# 确保终端支持 UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 设置 API key
export DEEPSEEK_API_KEY='sk-xxxxx'

# 运行客户端
python3 mcp_client.py
```

### 测试中文对话
```
👤 You: 如何下载 openEuler？
👤 You: 有哪些文档资源？
👤 You: 安全中心在哪里？
```

## 常见问题

### Q: 仍然出现编码错误怎么办？
A: 检查以下几点：
1. 确认终端支持 UTF-8: `locale` 命令查看
2. 确认 Python 版本 >= 3.7
3. 尝试重启终端会话

### Q: 为什么搜索中文找不到结果？
A: openEuler 官网主要是英文内容，中文关键词可能匹配较少。可以尝试：
- 使用英文关键词（如 "download" 而不是 "下载"）
- 搜索特定的中文页面 URL

### Q: 如何确认编码设置正确？
A: 运行以下命令：
```bash
python3 -c "import sys; print(sys.stdin.encoding, sys.stdout.encoding)"
```
应该输出: `utf-8 utf-8`

## 技术细节

### 编码流程
```
用户输入(UTF-8) → Python stdin(UTF-8) → MCP Client(UTF-8) →
MCP Server(UTF-8) → 工具处理(UTF-8) → 返回结果(UTF-8) →
DeepSeek API(UTF-8) → 显示输出(UTF-8)
```

### 关键点
- 所有文本数据使用 UTF-8 编码
- JSON 序列化保留非 ASCII 字符
- 错误处理使用 `errors='replace'` 避免崩溃
- stdio 流在程序启动时重新配置为 UTF-8

## 总结

✅ 已修复中文编码问题
✅ 添加完整的 UTF-8 支持
✅ 改进错误处理机制
✅ 通过中文测试验证

现在系统完全支持中文输入和输出！
