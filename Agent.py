import openai
import os
import sys
import subprocess
from dotenv import load_dotenv


# 1. 配置 API Key 和 基础路径
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
user_name = os.getenv("USER_NAME")

client = openai.OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com/v1"
)

# 从 Agent.md 读取系统提示词
def load_system_prompt():
    """从 Agent.md 文件读取系统提示词"""
    try:
        with open("Agent.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("错误：找不到 Agent.md 文件")
        sys.exit(1)

SYSTEM_PROMPT = load_system_prompt()

class ChatContext:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.model = "deepseek-reasoner"
        self.thinking = "enabled"
        self.total_tokens = 0

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def add_message(self, content, role = "user"):
        self.messages.append({"role": role, "content": content})


def agent_help(args, ctx):
    print("")

def agent_tokens(args, ctx):
    print(f"已使用token量: {ctx.total_tokens}\n" )

def agent_quit(args, ctx):
    print("---退出MyAgent---\n")
    print(f"本次使用token量: {ctx.total_tokens}\n")
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


def execute_powershell_command(command):

    #执行PowerShell命令并返回结果
    try:
        result = subprocess.run(
            ['powershell', '-Command', command],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        output = result.stdout + result.stderr
        return output
    except Exception as e:
        return f"执行命令时出错: {str(e)}"


def parse_and_process_response(ai_reply, ctx):

    # 获取第一行
    first_line_end = ai_reply.find('\n')
    if first_line_end == -1:
        first_line = ai_reply.strip()
    else:
        first_line = ai_reply[:first_line_end].strip()
    
    # 根据第一行第一个词判断响应类型
    if first_line.startswith("command:"):
        # 解析 command: <cmd> --explain: <explanation>
        parts = first_line.split(" --explain:", 1)
        command = parts[0][8:].strip()
        explanation = parts[1].strip() if len(parts) > 1 else "执行命令"
        
        print(f"\n{ctx.model}: {explanation}\n")
        print(f"[待执行命令] {command}")
        
        # 获取用户确认
        while True:
            user_confirm = input("是否执行此命令? (y/n): ").strip().lower()
            if user_confirm in ['y', 'n']:
                break
            print("请输入 y 或 n")
        
        # if safty_mode == False:

        if user_confirm == 'y':
            print("\n[执行中...]\n")
            cmd_output = execute_powershell_command(command)
            print(f"Powershell: \n{cmd_output}")
            
            # 将命令结果反馈给LLM
            ctx.add_message(f"命令执行结果:\n命令: {command}\n输出:\n{cmd_output}")
            
            # 继续与AI交互获取下一步指令
            response = get_response(ctx)
            ai_next_reply = response.choices[0].message.content
            ctx.add_message(ai_next_reply, role="assistant")
            #print(ai_next_reply)
            
            # 递归处理下一个响应
            is_complete, result = parse_and_process_response(ai_next_reply, ctx)
            if is_complete:
                return True, result
            return False, ""
        else:
            print("命令已取消\n")
            # 告诉AI用户取消了命令
            new_input = "用户取消了命令执行"
            feedback = input("请给出修改要求(可以为空): ").strip()
            if feedback:
                new_input += f",用户给出修改要求: {feedback}"
            ctx.add_message(new_input)
            response = get_response(ctx)
            ai_next_reply = response.choices[0].message.content
            ctx.add_message(ai_next_reply, role="assistant")
            #print(ai_next_reply)
            
            # 递归处理下一个响应
            is_complete, result = parse_and_process_response(ai_next_reply, ctx)
            if is_complete:
                return True, result
            return False, ""
    
    elif first_line.startswith("complete:"):
        # 提取complete后的内容
        final_result = first_line[9:].strip()
        print(f"{ctx.model}: [任务完成] {final_result}\n")
        return True, final_result
    
    elif first_line.startswith("reply:"):
        # 作为reply处理，输出整个回复
        print(ai_reply)
        return False, ""
    
    else:
        # 如果不匹配任何格式，作为普通回复输出
        print(ai_reply)
        return False, ""


ctx = ChatContext()

while True :
    user_input = input(f"\n>>>{user_name}:").strip()
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
        #print(ai_reply)
        
        # 处理AI的响应（命令执行、回复等）
        is_complete, _ = parse_and_process_response(ai_reply, ctx)