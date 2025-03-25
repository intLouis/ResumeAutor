# Please install OpenAI SDK first: `pip3 install openai`
from openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchRun

client = OpenAI(api_key="sk-a6ca73fb7c7b4f549d9ff068f37b9b26", base_url="https://api.deepseek.com")


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
