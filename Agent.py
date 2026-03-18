import openai
import os
import sys
from dotenv import load_dotenv


# 1. 配置 API Key 和 基础路径
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com/v1"
)

class ChatContext:
    def __init__(self):
        self.messages = [{"role": "system", "content": "你是一个得力的助手。"}]
        self.model = "deepseek-reasoner"
        self.thinking = "enabled"
        self.total_tokens = 0

    def reset(self):
        self.messages = [{"role": "system", "content": "你是一个得力的助手。"}]

    def add_message(self, content, role = "user"):
        self.messages.append({"role": role, "content": content})


def agent_help(args, ctx):
    print("")

def agent_tokens(args, ctx):
    print(f"已使用token量: {ctx.total_tokens}\n" )

def agent_quit(args, ctx):
    print("---退出MyAgent---\n")
    sys.exit(0)

def messages_init(args, ctx):
    ctx.reset()
    print("上下文初始化成功\n")

def messages_zip(args, ctx):
    ctx.add_message("总结压缩以上对话，保留重要内容，删减不必要内容")
    response = get_response(ctx)
    #print(response.choices[0].message.content)
    ctx.reset()
    ctx.add_message(f"这是之前的对话总结: {response.choices[0].message.content}", role = "assistant")
    print("上下文压缩成功\n")

commands ={
    "help": agent_help,
    "tokens": agent_tokens,
    "token":agent_tokens,
    "init": messages_init,
    "clear": messages_init, 
    "zip": messages_zip,
    "quit": agent_quit,
    "exit": agent_quit
}


def get_response(ctx):
    response = client.chat.completions.create(
        model=ctx.model, 
        messages=ctx.messages,
        extra_body={"thinking": {"type": ctx.thinking}}
    )
    ctx.total_tokens += response.usage.total_tokens
    return response


ctx = ChatContext()

while True :
    user_input = input("\n>>>用户:").strip()
    if not user_input:
        continue

    tokens = user_input.split()
    
    if tokens[0] == "agent":
        if len(tokens) == 1:
            agent_help([], ctx)
        else:
            command = tokens[1].lower()
            args = tokens[2:]
            if command in commands:
                commands[command](args, ctx)
            else:
                print("未找到命令: " + command + "\n输入 agent help 查询指令\n")

    else:
        ctx.add_message(user_input)
        response = get_response(ctx)
        ai_reply = response.choices[0].message.content
        ctx.add_message(ai_reply, role = "assistant")
        print(ai_reply)