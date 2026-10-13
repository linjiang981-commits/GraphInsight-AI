from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RagRequest(BaseModel):

    retrieval_mode: Literal["vector", "hybrid"] = "vector"

    @field_validator("question")
    @classmethod
    def reject_blank_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question cannot be blank")
        return value

    question: str = Field(
        min_length=1
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10
    )

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0
    )


class RagSource(BaseModel):

    id: int

    rank: int

    document_name: str

    chunk_index: int

    score: float

    content: str


class RagResponse(BaseModel):

    answer: str

    sources: list[RagSource]
