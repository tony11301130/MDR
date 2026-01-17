import requests
import os
from dotenv import load_dotenv

load_dotenv("ai_orchestration_engine/.env")
api_key = os.getenv("OPENAI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    models = response.json()
    for m in models.get('models', []):
        print(f"Model: {m['name']} - Methods: {m['supportedGenerationMethods']}")
else:
    print(f"Error: {response.text}")
