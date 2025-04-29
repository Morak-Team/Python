from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

api_key = os.getenv("OPEN_API_KEY")

# 새로운 OpenAI client 객체 생성
client = OpenAI(api_key=api_key)

# API 호출
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke about cats."}
    ]
)

print(response.choices[0].message.content)
