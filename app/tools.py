from langchain.tools import tool
import subprocess

@tool
def run_shell(command: str) -> str:
    """Run a shell command on the server"""
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True
    )
    return result.stdout or result.stderr

