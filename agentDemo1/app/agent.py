from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.tools import run_shell
from app.memory import memory

llm = ChatOpenAI(model="deepseek-chat", temperature=0)

def agent_node(state):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": messages + [response]}

graph = StateGraph(state_schema=dict)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.set_finish_point("agent")

agent = graph.compile(checkpointer=memory)

