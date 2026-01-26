'''
import os
from anthropic import Anthropic

def call_claude(prompt:str, system_prompt:str) -> str:
    """
    Calls the Claude API with the given prompt and system prompt.

    Args:
        prompt (str): The user prompt to send to Claude.
        system_prompt (str): The system prompt to set the context for Claude.

    Returns:
        str: The response from Claude.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1500,
        system=system_prompt,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text

def write_file(file_path:str, content:str) -> None:
    """
    Writes the given content to a file at the specified path.

    Args:
        file_path (str): The path to the file where content should be written.
        content (str): The content to write to the file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)
'''

import os
from openai import OpenAI

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")

def call_deepseek(prompt:str, system_prompt:str) -> str:
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1500
    )
    return response.choices[0].message.content
    
def call_llm(prompt:str, system_prompt:str) -> str:
    if LLM_PROVIDER == "deepseek":
        return call_deepseek(prompt, system_prompt)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER : {LLM_PROVIDER}")
    

def write_file(file_path:str, content:str) -> None:
    """
    Writes the given content to a file at the specified path.

    Args:
        file_path (str): The path to the file where content should be written.
        content (str): The content to write to the file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)