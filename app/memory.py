# app/memory.py
import sqlite3
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ModuleNotFoundError:
    from langgraph.checkpoint.sqlite_saver import SqliteSaver

# create sqlite3 connection
conn = sqlite3.connect(
        "agent_memory.db",
        check_same_thread=False
        )
# 
memory = SqliteSaver(conn)
