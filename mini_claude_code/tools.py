# tools.py
from pathlib import Path


WORKSPACE = Path("workspace")


def list_files():
    return "\n".join(str(p) for p in WORKSPACE.rglob("*") if p.is_file())


def read_file(path: str):
    file_path = WORKSPACE / path
    return file_path.read_text()


def write_file(path: str, content: str):
    file_path = WORKSPACE / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return "ok"

