#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test for the MCP system with Chinese support
"""
import asyncio
import sys
import os

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

async def run_comprehensive_test():
    """Run comprehensive tests"""
    print("=" * 60)
    print("  openEuler MCP 系统综合测试")
    print("  Comprehensive System Test")
    print("=" * 60)

    # Test 1: Check environment
    print("\n[测试 1] 检查环境配置")
    print(f"  Python 版本: {sys.version.split()[0]}")
    print(f"  stdin 编码: {sys.stdin.encoding}")
    print(f"  stdout 编码: {sys.stdout.encoding}")
    print(f"  默认编码: {sys.getdefaultencoding()}")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        print(f"  ✓ DEEPSEEK_API_KEY: 已设置 ({api_key[:10]}...)")
    else:
        print("  ⚠️  DEEPSEEK_API_KEY: 未设置")

    # Test 2: MCP Server connection
    print("\n[测试 2] MCP 服务器连接")
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
            env=None
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()
                tools = response.tools

                print(f"  ✓ 连接成功")
                print(f"  ✓ 可用工具: {len(tools)} 个")
                for tool in tools:
                    print(f"    - {tool.name}")

                # Test 3: Chinese query
                print("\n[测试 3] 中文查询测试")
                test_queries = ["下载", "文档", "社区"]

                for query in test_queries:
                    try:
                        result = await session.call_tool("search_openeuler", {
                            "query": query
                        })
                        content = result.content[0].text
                        print(f"  ✓ 查询 '{query}': 成功 ({len(content)} 字符)")
                    except Exception as e:
                        print(f"  ✗ 查询 '{query}': 失败 - {e}")

                # Test 4: English query
                print("\n[测试 4] 英文查询测试")
                test_queries = ["download", "documentation", "community"]

                for query in test_queries:
                    try:
                        result = await session.call_tool("search_openeuler", {
                            "query": query
                        })
                        content = result.content[0].text
                        print(f"  ✓ Query '{query}': Success ({len(content)} chars)")
                    except Exception as e:
                        print(f"  ✗ Query '{query}': Failed - {e}")

                # Test 5: Get page content
                print("\n[测试 5] 页面内容获取")
                try:
                    result = await session.call_tool("get_page_content", {
                        "url": "https://www.openeuler.org"
                    })
                    content = result.content[0].text
                    print(f"  ✓ 获取主页内容: 成功 ({len(content)} 字符)")
                except Exception as e:
                    print(f"  ✗ 获取主页内容: 失败 - {e}")

                print("\n" + "=" * 60)
                print("✅ 所有测试完成！")
                print("=" * 60)

                if not api_key:
                    print("\n⚠️  提示: 设置 DEEPSEEK_API_KEY 后可以使用完整功能")
                    print("   export DEEPSEEK_API_KEY='your-api-key-here'")
                else:
                    print("\n✓ 系统已就绪，可以运行:")
                    print("   python3 mcp_client.py")

                return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(run_comprehensive_test())
    sys.exit(0 if result else 1)
