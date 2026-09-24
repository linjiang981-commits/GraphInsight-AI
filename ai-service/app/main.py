from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService


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
        request.question
    )

    return ChatResponse(
        answer=answer
    )