# main.py
from agent import Agent

if __name__ == "__main__":
    agent = Agent()

    agent.run(
        "Create a Python file demo.py that prints 'hello from agent'. "
        "If the file exists, update it."
    )

