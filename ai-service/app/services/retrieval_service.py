import json
from pathlib import Path

import numpy as np

from app.services.embedding_service import (
    EmbeddingService
)


class RetrievalService:

    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )

        data_path = (
            Path(__file__).resolve()
            .parents[2]
            / "data"
            / "network_documents.json"
        )

        with open(
            data_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.documents = json.load(file)

        texts = [
            document["content"]
            for document in self.documents
        ]

        self.document_embeddings = (
            self.embedding_service.encode(texts)
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

        scores = np.dot(
            self.document_embeddings,
            query_embedding
        )

        top_indices = np.argsort(
            scores
        )[::-1][:top_k]

        results = []

        for index in top_indices:

            document = self.documents[
                int(index)
            ]

            results.append(
                {
                    "id": document["id"],
                    "content": document["content"],
                    "score": float(
                        scores[index]
                    )
                }
            )

        return results