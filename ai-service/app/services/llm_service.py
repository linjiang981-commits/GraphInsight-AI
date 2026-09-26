import json
import os

import httpx
from dotenv import load_dotenv

from app.schemas.chat import ChatMessage


load_dotenv()


SYSTEM_PROMPT = """
You are GraphInsight AI.

You are an intelligent assistant for enterprise
knowledge retrieval and network troubleshooting.

Answer questions clearly and accurately.
If you do not know something, say that you do not know.
""".strip()


class LLMService:

    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL")
        self.api_key = os.getenv("LLM_API_KEY")
        self.model = os.getenv("LLM_MODEL")

        if not self.base_url:
            raise ValueError(
                "LLM_BASE_URL is not configured"
            )

        if not self.api_key:
            raise ValueError(
                "LLM_API_KEY is not configured"
            )

        if not self.model:
            raise ValueError(
                "LLM_MODEL is not configured"
            )

    def _build_messages(
        self,
        messages: list[ChatMessage]
    ) -> list[dict]:

        result = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        for message in messages:
            result.append(
                {
                    "role": message.role,
                    "content": message.content
                }
            )

        return result

    def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.3
    ) -> str:

        url = (
            f"{self.base_url.rstrip('/')}"
            "/chat/completions"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self._build_messages(
                messages
            ),
            "temperature": temperature
        }

        with httpx.Client(
            timeout=60.0
        ) as client:

            response = client.post(
                url,
                headers=headers,
                json=payload
            )

            response.raise_for_status()

            data = response.json()

        usage = data.get("usage")

        if usage:
            print(
                "Token Usage:",
                usage
            )

        return (
            data["choices"][0]
            ["message"]
            ["content"]
        )

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.3
    ):

        url = (
            f"{self.base_url.rstrip('/')}"
            "/chat/completions"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self._build_messages(
                messages
            ),
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(
            timeout=60.0
        ) as client:

            async with client.stream(
                "POST",
                url,
                headers=headers,
                json=payload
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if not line.startswith("data:"):
                        continue

                    data_text = line[5:].strip()

                    if data_text == "[DONE]":
                        break

                    try:
                        chunk = json.loads(
                            data_text
                        )
                    except json.JSONDecodeError:
                        continue

                    delta = (
                        chunk["choices"][0]
                        .get("delta", {})
                        .get("content")
                    )

                    if delta:
                        yield delta