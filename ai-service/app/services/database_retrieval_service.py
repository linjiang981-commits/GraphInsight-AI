from app.services.embedding_service import (
    EmbeddingService
)

from app.services.vector_store import (
    VectorStore
)

from app.services.bm25_service import (
    BM25Service
)



class DatabaseRetrievalService:


    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )


        self.vector_store = (
            VectorStore()
        )


        self.bm25_service = (
            BM25Service()
        )



    # ==================================
    # Vector Only Retrieval
    # 保留作为Baseline
    # ==================================

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


        results = (
            self.vector_store
            .similarity_search(
                query_embedding,
                top_k
            )
        )


        return results



    # ==================================
    # Hybrid Retrieval
    # Vector + BM25
    # ==================================

    def hybrid_search(
        self,
        query: str,
        top_k: int = 3
    ):


        # --------------------------
        # 1. Vector召回
        # --------------------------

        vector_results = (
            self.search(
                query,
                top_k * 2
            )
        )


        # --------------------------
        # 2. BM25召回
        # --------------------------

        bm25_results = (
            self.bm25_service.search(
                query,
                top_k * 2
            )
        )


        # --------------------------
        # 3. 融合
        # --------------------------

        results = (
            self._merge_results(
                vector_results,
                bm25_results
            )
        )


        return results[:top_k]



    # ==================================
    # Hybrid Fusion
    # ==================================

    def _merge_results(
        self,
        vector_results,
        bm25_results
    ):


        result_map = {}



        # --------------------------
        # Vector Score
        # --------------------------

        for item in vector_results:


            doc_id = item["id"]


            result_map[doc_id] = {

                "id":
                    item["id"],


                "document_id":
                    item.get(
                        "document_id"
                    ),


                "chunk_index":
                    item.get(
                        "chunk_index"
                    ),


                "content":
                    item["content"],


                "metadata":
                    item.get(
                        "metadata"
                    ),


                "vector_score":
                    item["score"],


                "bm25_score":
                    0

            }



        # --------------------------
        # BM25 Score
        # --------------------------

        for item in bm25_results:


            doc_id = item["id"]


            if doc_id in result_map:


                result_map[doc_id][
                    "bm25_score"
                ] = item["score"]


            else:


                result_map[doc_id] = {

                    "id":
                        item["id"],


                    "document_id":
                        item.get(
                            "document_id"
                        ),


                    "chunk_index":
                        item.get(
                            "chunk_index"
                        ),


                    "content":
                        item["content"],


                    "metadata":
                        item.get(
                            "metadata"
                        ),


                    "vector_score":
                        0,


                    "bm25_score":
                        item["score"]

                }



        # --------------------------
        # Score融合
        #
        # 当前简单加权
        # 后续可以升级RRF
        # --------------------------

        results=[]



        for item in result_map.values():


            hybrid_score = (

                0.5 *
                item["vector_score"]

                +

                0.5 *
                item["bm25_score"]

            )


            results.append(

                {

                    "id":
                        item["id"],


                    "document_id":
                        item[
                            "document_id"
                        ],


                    "chunk_index":
                        item[
                            "chunk_index"
                        ],


                    "content":
                        item[
                            "content"
                        ],


                    "metadata":
                        item[
                            "metadata"
                        ],


                    "score":
                        hybrid_score

                }

            )



        # 按融合分数排序

        results.sort(

            key=lambda x:x["score"],

            reverse=True

        )


        return results