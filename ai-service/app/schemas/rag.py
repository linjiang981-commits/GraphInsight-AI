from pydantic import BaseModel, Field


class RagRequest(BaseModel):

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

    rank: int

    document_name: str

    chunk_index: int

    score: float

    content: str


class RagResponse(BaseModel):

    answer: str

    sources: list[RagSource]