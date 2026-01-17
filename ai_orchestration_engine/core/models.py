from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLM(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        """發送對話請求到 LLM。"""
        pass

class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        return self.client.chat.completions.create(**kwargs)

class GeminiLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model
        # 確保模型名稱格式正確 (例如 gemini-1.5-flash)
        model_id = model if model.startswith("models/") else f"models/{model}"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent?key={api_key}"

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        import requests
        import json

        # 將訊息轉換為 Gemini API 格式
        contents = []
        system_instruction = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                content_text = msg["content"]
                # 如果有 system instruction，將其併入第一個 user message
                if system_instruction and not contents:
                    content_text = f"System Instruction: {system_instruction}\n\nUser Message: {content_text}"
                    system_instruction = "" # 確保只加一次
                
                contents.append({
                    "role": role,
                    "parts": [{"text": content_text}]
                })

        payload = {
            "contents": contents
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.url, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            raise Exception(f"Gemini API Error: {response.status_code} - {response.text}")
            
        data = response.json()
        
        # 提取文字內容
        try:
            text_content = data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexWarning):
            text_content = "AI 未能提供有效回應。"

        # 模擬 OpenAI 的結構
        class MockChoice:
            def __init__(self, content):
                class MockMessage:
                    def __init__(self, content):
                        self.content = content
                        self.tool_calls = None
                self.message = MockMessage(content)
        
        class MockResponse:
            def __init__(self, content):
                self.choices = [MockChoice(content)]
        
        return MockResponse(text_content)
