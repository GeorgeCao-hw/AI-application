#!/usr/bin/env python3
"""
Test MCP client connection without requiring DeepSeek API
"""
import asyncio
import sys
import os

# Mock the OpenAI client for testing
class MockOpenAI:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

# Temporarily replace OpenAI import
sys.modules['openai'] = type(sys)('openai')
sys.modules['openai'].OpenAI = MockOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_connection():
    """Test MCP server connection"""
    print("Testing MCP server connection...")

    try:
        server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
            env=None
        )

        # Use async context manager correctly
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # List tools
                response = await session.list_tools()
                tools = response.tools

                print(f"✓ Successfully connected to MCP server")
                print(f"✓ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:60]}...")

                return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mcp_connection())
    sys.exit(0 if result else 1)
