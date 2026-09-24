import os

import httpx
from dotenv import load_dotenv


load_dotenv()


class LLMService:

    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL")
        self.api_key = os.getenv("LLM_API_KEY")
        self.model = os.getenv("LLM_MODEL")

        if not self.base_url:
            raise ValueError("LLM_BASE_URL is not configured")

        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured")

        if not self.model:
            raise ValueError("LLM_MODEL is not configured")

    def chat(self, question: str) -> str:

        url = f"{self.base_url.rstrip('/')}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are GraphInsight AI."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            "temperature": 0.3
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                headers=headers,
                json=payload
            )

            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]