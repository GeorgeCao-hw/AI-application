#!/usr/bin/env python3
"""
Test script for MCP server functionality
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server import fetch_page_content, search_content

async def test_server():
    """Test MCP server functions"""
    print("Testing MCP Server Functions")
    print("=" * 60)

    # Test 1: Fetch page content
    print("\n1. Testing fetch_page_content...")
    try:
        result = await fetch_page_content("https://www.openeuler.org")
        print(f"   ✓ Title: {result.get('title', 'N/A')}")
        print(f"   ✓ Content length: {len(result.get('content', ''))} chars")
        print(f"   ✓ Links found: {len(result.get('links', []))}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Search content
    print("\n2. Testing search_content...")
    try:
        result = await search_content("download")
        print(f"   ✓ Query: {result.get('query')}")
        print(f"   ✓ Matches found: {result.get('matches_found', 0)}")
        print(f"   ✓ Relevant links: {len(result.get('relevant_links', []))}")
        if result.get('relevant_links'):
            print(f"   ✓ First link: {result['relevant_links'][0]['text']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("✓ Server tests completed!")

if __name__ == "__main__":
    asyncio.run(test_server())
