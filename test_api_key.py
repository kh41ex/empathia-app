# test_api_key.py
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key: {api_key}")
print(f"Key length: {len(api_key) if api_key else 0}")
print(f"Key starts with: {api_key[:10] if api_key else 'None'}")