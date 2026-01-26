#from tools import call_claude, write_file
from tools import call_llm, write_file
 
SYSTEM_PROMPT = """
你是一名资深 Python Web 开发工程师。
你的任务是根据需求生成【可直接运行的最小 Demo】。
请只输出完整代码，不要解释。
"""

class CodeGenAgent:
    def __init__(self, workspace:str):
        self.workspace = workspace
    
    def run(self, user_request:str) -> str:
        #code = call_claude(
        code = call_llm(
            prompt=user_request,
            system_prompt=SYSTEM_PROMPT
        )
        output_path = f"{self.workspace}/demo.py"
        write_file(output_path, code)
        return f"File written to {output_path}"