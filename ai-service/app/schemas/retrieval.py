from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):

    query: str

    top_k: int = Field(
        default=3,
        ge=1,
        le=10
    )


class RetrievalResult(BaseModel):

    id: int
    content: str
    score: float


class RetrievalResponse(BaseModel):

    results: list[RetrievalResult]