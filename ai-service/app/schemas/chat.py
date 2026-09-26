from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        min_length=1
    )

    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0
    )


class ChatResponse(BaseModel):
    answer: str