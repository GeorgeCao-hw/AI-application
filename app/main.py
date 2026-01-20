from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import agent
from langchain_core.messages import HumanMessage

app = FastAPI()

class RunRequest(BaseModel):
    prompt: str
    session_id: str


@app.post("/run")
def run_agent(req: RunRequest):
    result = agent.invoke(
    {
        "messages": [HumanMessage(content=req.prompt)]
    },
    config ={
        "configurable":{
            "thread_id":req.session_id
            }
        }
    )
    return {
            "reply": result["messages"][-1].content
    }

