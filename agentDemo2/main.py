from dotenv import load_dotenv
from agent import CodeGenAgent

def main():
    load_dotenv()
    
    agent = CodeGenAgent(workspace="./workspace")
    user_request = input("请输入你的需求: \n")
    output_file = agent.run(user_request)

    print(f"\n 代码已经生产：{output_file}")

if __name__ == "__main__":
    main() 
