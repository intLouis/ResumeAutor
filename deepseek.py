import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载配置文件
load_dotenv("config.env")

# 从环境变量获取 API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_api_key_here":
    print("警告: 请在 config.env 文件中配置 DEEPSEEK_API_KEY")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


#  实现deepseek api调用
def chat(prompt: str, system_prompt=None):
    messages = [
        {"role": "user", "content": prompt},
    ]

    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=False
    )

    return response.choices[0].message.content
