import requests
import json
import os
from dotenv import load_dotenv

load_dotenv("ai_orchestration_engine/.env")
api_key = os.getenv("OPENAI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
headers = {'Content-Type': 'application/json'}
payload = {
    "contents": [{
        "parts": [{"text": "Hello, are you working?"}]
    }]
}

print(f"Testing URL: {url.replace(api_key, 'REDACTED')}")
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
