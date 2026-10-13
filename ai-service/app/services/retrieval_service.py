import json
from pathlib import Path

import numpy as np

from app.services.embedding_service import (
    EmbeddingService
)

from app.services.bm25_service import (
    BM25Service
)


class RetrievalService:


    def __init__(self):

        # Embedding服务
        self.embedding_service = (
            EmbeddingService()
        )


        # ===============================
        # 加载文档
        # ===============================

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



        # ===============================
        # Vector Retrieval索引
        # ===============================

        self.document_embeddings = (
            self.embedding_service.encode(
                texts
            )
        )



        # ===============================
        # BM25 Retrieval索引
        # ===============================

        self.bm25_service = BM25Service()


        self.bm25_service.build_index(
            texts
        )



    # ==================================================
    # 原始向量检索
    # Vector Only Retrieval
    # ==================================================

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
                    ),

                    "source": "vector"
                }
            )



        return results




    # ==================================================
    # Hybrid Retrieval
    # Vector + BM25
    # ==================================================

    def hybrid_search(
        self,
        query: str,
        top_k: int = 3
    ):


        scores = {}


        documents_map = {
            doc["id"]: doc
            for doc in self.documents
        }



        # =========================
        # 1. Vector Search
        # =========================

        vector_results = self.search(
            query,
            top_k
        )


        for item in vector_results:

            doc_id = item["id"]

            scores[doc_id] = {

                "vector_score":
                    item["score"],

                "bm25_score":
                    0,

                "content":
                    item["content"]

            }



        # =========================
        # 2. BM25 Search
        # =========================

        bm25_results = (
            self.bm25_service.search(
                query,
                top_k
            )
        )



        for content, score in bm25_results:


            for doc in self.documents:


                if doc["content"] == content:


                    doc_id = doc["id"]


                    if doc_id not in scores:

                        scores[doc_id] = {

                            "vector_score":0,

                            "bm25_score":
                                float(score),

                            "content":
                                content
                        }

                    else:

                        scores[doc_id][
                            "bm25_score"
                        ] = float(score)


                    break



        # =========================
        # 3. Hybrid Score
        # =========================

        results=[]


        for doc_id,item in scores.items():


            hybrid_score = (

                0.5 *
                item["vector_score"]

                +

                0.5 *
                item["bm25_score"]

            )


            results.append(

                {
                    "id":doc_id,

                    "content":
                        item["content"],

                    "score":
                        hybrid_score

                }

            )



        # =========================
        # 4. 排序
        # =========================

        results.sort(

            key=lambda x:x["score"],

            reverse=True

        )


        return results[:top_k]