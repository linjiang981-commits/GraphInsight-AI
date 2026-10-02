from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from fastapi.responses import StreamingResponse
from app.schemas.retrieval import (
    RetrievalRequest,
    RetrievalResponse
)

from app.services.retrieval_service import (
    RetrievalService
)

from app.schemas.rag import (
    RagRequest,
    RagResponse
)

from app.services.rag_service import (
    RagService
)


app = FastAPI(
    title="GraphInsight AI Service",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


llm_service = LLMService()

rag_service = RagService()

retrieval_service = RetrievalService()


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "graphinsight-ai-service"
    }


@app.post(
    "/api/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    answer = llm_service.chat(
        messages=request.messages,
        temperature=request.temperature
    )

    return ChatResponse(
        answer=answer
    )

@app.post("/api/chat/stream")
async def chat_stream(
    request: ChatRequest
):

    return StreamingResponse(
        llm_service.stream_chat(
            messages=request.messages,
            temperature=request.temperature
        ),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache"
        }
    )

@app.post(
    "/api/retrieval/search",
    response_model=RetrievalResponse
)
def retrieval_search(
    request: RetrievalRequest
):

    results = retrieval_service.search(
        query=request.query,
        top_k=request.top_k
    )

    return RetrievalResponse(
        results=results
    )

@app.post(
    "/api/rag/query",
    response_model=RagResponse
)
def rag_query(
    request: RagRequest
):

    result = rag_service.answer(
        question=request.question,
        top_k=request.top_k,
        temperature=request.temperature
    )

    return RagResponse(
        **result
    )