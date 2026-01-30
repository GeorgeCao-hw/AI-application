#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server for openEuler website content search
"""
import asyncio
import json
import sys
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx
from bs4 import BeautifulSoup
import re

# Ensure UTF-8 encoding for stdio
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

# Initialize MCP server
app = Server("openeuler-search")

# Cache for website content
content_cache = {}

async def fetch_page_content(url: str) -> dict:
    """Fetch and parse webpage content"""
    if url in content_cache:
        return content_cache[url]

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True)
                if link_text and href:
                    links.append({"text": link_text, "url": href})

            result = {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "content": text[:5000],  # Limit content size
                "links": links[:50]  # Limit number of links
            }

            content_cache[url] = result
            return result

    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "content": "",
            "links": []
        }

async def search_content(query: str, url: str = "https://www.openeuler.org") -> dict:
    """Search for content on the website"""
    page_data = await fetch_page_content(url)

    if "error" in page_data:
        return page_data

    # Simple search in content
    content = page_data["content"].lower()
    query_lower = query.lower()

    matches = []
    if query_lower in content:
        # Find context around matches
        pattern = re.compile(f'.{{0,100}}{re.escape(query_lower)}.{{0,100}}', re.IGNORECASE)
        for match in pattern.finditer(page_data["content"]):
            matches.append(match.group())

    # Search in links
    relevant_links = [
        link for link in page_data["links"]
        if query_lower in link["text"].lower() or query_lower in link["url"].lower()
    ]

    return {
        "query": query,
        "url": url,
        "title": page_data["title"],
        "matches_found": len(matches),
        "match_snippets": matches[:5],
        "relevant_links": relevant_links[:10]
    }

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_openeuler",
            description="Search for content on the openEuler website. Returns matching text snippets and relevant links.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'download', 'documentation', 'security')"
                    },
                    "url": {
                        "type": "string",
                        "description": "Specific URL to search (default: https://www.openeuler.org)",
                        "default": "https://www.openeuler.org"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_page_content",
            description="Fetch and return the full content of a specific openEuler webpage including title, text content, and all links.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the page to fetch"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="get_main_sections",
            description="Get the main sections and navigation structure of the openEuler website.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "search_openeuler":
        query = arguments.get("query", "")
        url = arguments.get("url", "https://www.openeuler.org")

        result = await search_content(query, url)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

    elif name == "get_page_content":
        url = arguments.get("url", "https://www.openeuler.org")
        result = await fetch_page_content(url)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

    elif name == "get_main_sections":
        # Return predefined main sections based on website structure
        sections = {
            "main_sections": [
                {
                    "name": "Download",
                    "description": "Access to community and commercial releases",
                    "url": "https://www.openeuler.org/download/"
                },
                {
                    "name": "Documentation",
                    "description": "Comprehensive technical guides",
                    "url": "https://docs.openeuler.org"
                },
                {
                    "name": "Security Center",
                    "description": "Security advisories and updates",
                    "url": "https://www.openeuler.org/security/"
                },
                {
                    "name": "Migration Center",
                    "description": "Migration guidance and tools",
                    "url": "https://www.openeuler.org/migration/"
                },
                {
                    "name": "Community",
                    "description": "SIGs, contribution guidelines, and member information",
                    "url": "https://www.openeuler.org/community/"
                },
                {
                    "name": "Events",
                    "description": "Community events and news",
                    "url": "https://www.openeuler.org/events/"
                }
            ]
        }
        return [TextContent(
            type="text",
            text=json.dumps(sections, indent=2, ensure_ascii=False)
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
