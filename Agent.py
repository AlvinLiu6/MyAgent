import openai
import os
from dotenv import load_dotenv


# 1. 配置 API Key 和 基础路径
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com/v1" # 如果用国内模型，这里换成对应的 URL
)

# 2. 发起对话请求
messages = [ {"role": "system", "content": "你是一个得力的助手。"}]
while True :
    user_input = input("\n用户:")
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="deepseek-reasoner", 
        messages=messages,
        extra_body={"thinking": {"type": "enabled"}}
    )

    # 3. 打印结果
    print(response.choices[0].message.content)