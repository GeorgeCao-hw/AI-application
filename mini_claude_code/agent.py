# agent.py
import json
from llm import LLM
import tools


SYSTEM_PROMPT = """
You are a coding agent like Claude Code.

Rules:
- You can use tools to inspect and modify files.
- Always decide the next action.
- When finished, reply with:
  {"action": "done"}

Available actions:
- list_files
- read_file
- write_file

When using an action, respond ONLY in JSON:
{
  "action": "...",
  "args": {...}
}

IMPORTANT:
- You MUST respond with a single valid JSON object.
- Do NOT include any text before or after the JSON.
- Do NOT explain your reasoning.
"""

def extract_json(text: str):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in LLM output")
    return json.loads(text[start:end + 1])


class Agent:
    def __init__(self):
        self.llm = LLM()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def step(self):
        reply = self.llm.chat(self.messages)
        print("\nLLM:", reply)

        action = extract_json(reply)
        name = action["action"]

        if name == "done":
            return False

        if name == "list_files":
            result = tools.list_files()
        elif name == "read_file":
            result = tools.read_file(**action["args"])
        elif name == "write_file":
            result = tools.write_file(**action["args"])
        else:
            raise ValueError(f"Unknown action: {name}")

        self.messages.append({"role": "assistant", "content": reply})
        self.messages.append({
            "role": "assistant",
            "content": f"Tool result:\n{result}"
        })


        return True

    def run(self, task: str):
        self.messages.append({"role": "user", "content": task})

        while self.step():
            pass

