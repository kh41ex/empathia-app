# test_api.py
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        max_tokens=50
    )
    print("✅ API is working!")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print("❌ API Error:", e)