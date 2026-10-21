from app.services.embedding_service import (
    EmbeddingService
)

from app.services.vector_store import (
    VectorStore
)


class DatabaseRetrievalService:


    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )

        self.vector_store = (
            VectorStore()
        )


    def search(
        self,
        query: str,
        top_k: int = 3
    ):

        query_embedding = (
            self.embedding_service.encode(
                [query]
            )[0]
        )

        return (
            self.vector_store
            .similarity_search(
                query_embedding,
                top_k
            )
        )