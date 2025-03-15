from openai import OpenAI

API_KEY = "sk-lCcFBBt7DE3wl6KDgPqKXBwdmqO9F5sd92YB8eTB33QGGeuV"
BASE_URL = "https://api.moonshot.cn/v1"

# AI 处理函数
def get_ai_response(user_question):
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手..."},
                {"role": "user", "content": user_question}
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content

    except Exception as e:
        return f"AI 请求失败: {str(e)}"