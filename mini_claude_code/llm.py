# llm.py
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import os


class LLM:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        self.client = OpenAI(
            api_key=api_key,            
            base_url="https://api.deepseek.com"
        )

    def chat(self, messages):
        response = self.client.chat.completions.create(
            model="deepseek-chat",            
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content

