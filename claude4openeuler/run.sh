#!/bin/bash

# openEuler MCP System Launcher

echo "=================================="
echo "  openEuler MCP System"
echo "=================================="
echo ""

# Check if DEEPSEEK_API_KEY is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ Error: DEEPSEEK_API_KEY is not set"
    echo ""
    echo "Please set your DeepSeek API key:"
    echo "  export DEEPSEEK_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import openai, mcp, httpx, bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✓ Dependencies OK"
echo ""

# Run the client
python3 mcp_client.py
