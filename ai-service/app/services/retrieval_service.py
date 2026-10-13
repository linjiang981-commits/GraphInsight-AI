import json
from pathlib import Path

import numpy as np

from app.services.bm25_service import BM25Service
from app.services.embedding_service import EmbeddingService
from app.services.hybrid_retriever import reciprocal_rank_fusion


class RetrievalService:
    def __init__(self, embedding_service=None):
        self.embedding_service = (
            embedding_service if embedding_service is not None
            else EmbeddingService()
        )
        path = (
            Path(__file__).resolve().parents[2]
            / "data" / "network_documents.json"
        )
        self.documents = json.loads(path.read_text(encoding="utf-8"))
        self.document_embeddings = (
            self.embedding_service.encode(
                [item["content"] for item in self.documents]
            )
            if self.documents else None
        )
        self.bm25_service = BM25Service()
        self.bm25_service.build_index(self.documents)

    def search(self, query: str, top_k: int = 3):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not query.strip() or not self.documents:
            return []

        query_embedding = self.embedding_service.encode([query])[0]
        scores = np.dot(self.document_embeddings, query_embedding)
        indices = sorted(
            range(len(self.documents)),
            key=lambda index: (-float(scores[index]), self.documents[index]["id"]),
        )
        return [
            {**self.documents[index], "score": float(scores[index])}
            for index in indices[:top_k]
        ]

    def hybrid_search(self, query: str, top_k: int = 3):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        candidate_k = max(6, top_k * 2)
        vector_results = self.search(query, candidate_k)
        bm25_results = self.bm25_service.search(query, candidate_k)
        return reciprocal_rank_fusion(
            [vector_results, bm25_results]
        )[:top_k]
