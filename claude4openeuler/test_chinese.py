#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Chinese character support in MCP communication
"""
import asyncio
import json
import sys

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_chinese_support():
    """Test Chinese character handling"""
    print("测试中文字符支持...")
    print("Testing Chinese character support...")

    try:
        server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
            env=None
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Test 1: Get main sections (no Chinese input)
                print("\n测试 1: 获取主要板块")
                result = await session.call_tool("get_main_sections", {})
                content = result.content[0].text
                print(f"✓ 返回内容长度: {len(content)} 字符")

                # Test 2: Search with Chinese query
                print("\n测试 2: 使用中文搜索")
                chinese_query = "下载"
                print(f"搜索关键词: {chinese_query}")

                result = await session.call_tool("search_openeuler", {
                    "query": chinese_query
                })

                content = result.content[0].text
                print(f"✓ 搜索成功，返回内容长度: {len(content)} 字符")

                # Parse and display result
                data = json.loads(content)
                print(f"✓ 查询: {data.get('query')}")
                print(f"✓ 找到匹配: {data.get('matches_found', 0)} 个")

                print("\n✅ 所有中文测试通过！")
                return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_chinese_support())
    sys.exit(0 if result else 1)
