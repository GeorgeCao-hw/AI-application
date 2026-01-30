#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client for openEuler website search with interactive chat interface
"""
import asyncio
import json
import sys
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ensure UTF-8 encoding for stdio
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

class OpenEulerChatClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.session = None
        self.conversation_history = []
        self.stdio_context = None
        self.session_context = None

    async def __aenter__(self):
        """Async context manager entry"""
        server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
            env=None
        )

        # Use async context manager for stdio_client
        self.stdio_context = stdio_client(server_params)
        stdio_transport = await self.stdio_context.__aenter__()
        read_stream, write_stream = stdio_transport

        # Create session
        self.session = ClientSession(read_stream, write_stream)
        self.session_context = self.session
        await self.session_context.__aenter__()

        # Initialize session
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        self.tools = response.tools
        print(f"✓ Connected to MCP server with {len(self.tools)} tools available\n")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session_context:
            await self.session_context.__aexit__(exc_type, exc_val, exc_tb)
        if self.stdio_context:
            await self.stdio_context.__aexit__(exc_type, exc_val, exc_tb)

    def format_tools_for_openai(self):
        """Format MCP tools for OpenAI-compatible API"""
        formatted_tools = []
        for tool in self.tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return formatted_tools

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

    async def chat(self, user_message: str):
        """Process a chat message"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Prepare system prompt
        system_prompt = """You are a helpful assistant that helps users find information on the openEuler website (https://www.openeuler.org).

You have access to tools that can:
1. Search for content on the website
2. Fetch specific page content
3. Get the main sections of the website

When users ask questions:
- Use the appropriate tools to find relevant information
- Provide clear, concise answers based on the tool results
- Include relevant URLs when available
- If you can't find specific information, suggest where the user might look

Always be helpful and guide users to the right resources on the openEuler website."""

        # Prepare messages with system prompt
        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

        # Call DeepSeek with tools
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=self.format_tools_for_openai(),
            max_tokens=4096
        )

        # Process response
        while response.choices[0].finish_reason == "tool_calls":
            # Extract tool calls
            tool_calls = response.choices[0].message.tool_calls

            # Add assistant message with tool calls to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in tool_calls
                ]
            })

            # Execute tool calls
            for tool_call in tool_calls:
                print(f"  🔧 Using tool: {tool_call.function.name}")
                try:
                    tool_input = json.loads(tool_call.function.arguments)
                    tool_result = await self.process_tool_call(tool_call.function.name, tool_input)

                    # Add tool result to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
                except json.JSONDecodeError as e:
                    print(f"  ⚠️  JSON decode error: {e}")
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": f"Invalid JSON: {str(e)}"}, ensure_ascii=False)
                    })
                except Exception as e:
                    print(f"  ⚠️  Tool execution error: {e}")
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                    })

            # Continue conversation
            messages = [{"role": "system", "content": system_prompt}] + self.conversation_history
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.format_tools_for_openai(),
                max_tokens=4096
            )

        # Extract final text response
        final_response = response.choices[0].message.content or ""

        # Add final response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })

        return final_response

    async def interactive_chat(self):
        """Run interactive chat loop"""
        print("=" * 60)
        print("  openEuler Website Search Assistant")
        print("=" * 60)
        print("\nAsk me anything about the openEuler website!")
        print("Type 'quit' or 'exit' to end the conversation.\n")

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Visit https://www.openeuler.org for more information.")
                    break

                print("\n🤖 Assistant: ", end="", flush=True)
                response = await self.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

async def main():
    """Main entry point"""
    import os

    # Get API key from environment
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export DEEPSEEK_API_KEY='your-api-key-here'")
        return

    # Create and run client using async context manager
    async with OpenEulerChatClient(api_key) as client:
        await client.interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())
