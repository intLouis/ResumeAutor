from openai import OpenAI

client = OpenAI(api_key="sk-773202bac62a4ab79fd47347566987ea", base_url="https://api.deepseek.com")


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
