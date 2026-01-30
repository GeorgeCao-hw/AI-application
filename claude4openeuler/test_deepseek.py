#!/usr/bin/env python3
"""
Simple test to verify DeepSeek API integration
"""
import os
from openai import OpenAI

def test_deepseek_api():
    """Test basic DeepSeek API call"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set")
        print("\nPlease set your API key:")
        print("  export DEEPSEEK_API_KEY='your-api-key-here'")
        return False

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        print("Testing DeepSeek API connection...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, DeepSeek!' if you can hear me."}
            ],
            max_tokens=50
        )

        result = response.choices[0].message.content
        print(f"✓ API Response: {result}")
        print("\n✓ DeepSeek API is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_deepseek_api()
