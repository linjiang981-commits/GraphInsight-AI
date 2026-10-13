from app.services.bm25_service import BM25Service
from app.services.embedding_service import EmbeddingService
from app.services.hybrid_retriever import reciprocal_rank_fusion
from app.services.vector_store import VectorStore


class DatabaseRetrievalService:
    def __init__(self, embedding_service=None, vector_store=None):
        self.embedding_service = (
            embedding_service if embedding_service is not None
            else EmbeddingService()
        )
        self.vector_store = vector_store if vector_store is not None else VectorStore()
        self.bm25_service = BM25Service()
        self.corpus = []

    def reload_bm25(self):
        corpus = self.vector_store.list_chunks()
        bm25_service = BM25Service()
        bm25_service.build_index(corpus)
        self.corpus = corpus
        self.bm25_service = bm25_service
        return bm25_service

    def search(self, query: str, top_k: int = 3):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not query.strip():
            return []
        embedding = self.embedding_service.encode([query])[0]
        return self.vector_store.similarity_search(embedding, top_k)

    def hybrid_search(self, query: str, top_k: int = 3):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not query.strip():
            return []
        # Small-demo strategy: rebuild from current database chunks per request.
        # This avoids stale BM25 results after document ingestion. For a large
        # corpus, replace this with a versioned index and explicit refresh.
        bm25_service = self.reload_bm25()
        candidate_k = max(6, top_k * 2)
        vector_results = self.search(query, candidate_k)
        bm25_results = bm25_service.search(query, candidate_k)
        return reciprocal_rank_fusion(
            [vector_results, bm25_results], rrf_k=60
        )[:top_k]
