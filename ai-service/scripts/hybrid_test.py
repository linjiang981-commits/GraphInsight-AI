from app.services.database_retrieval_service import DatabaseRetrievalService
from app.services.hybrid_retriever import reciprocal_rank_fusion


def show(label, results, canonical):
    print("\n", label)
    for rank, item in enumerate(results, start=1):
        original = canonical[item["id"]]
        for key in ["document_id", "chunk_index", "content", "metadata"]:
            assert item[key] == original[key], (item["id"], key)
        print(
            rank, "id=", item["id"],
            "source=", item["metadata"].get("document_name"),
            "chunk=", item["chunk_index"],
            "score=", round(item["score"], 6),
        )
        print(item["content"])


def main():
    service = DatabaseRetrievalService()
    service.reload_bm25()
    canonical = {item["id"]: item for item in service.corpus}
    questions = [
        "GI-NET-017 是什么意思？",
        "GI-NET-023 对应什么排查流程？",
        "测试环境 API 网关上游请求超时阈值是多少？",
        "健康检查连续失败多少次触发告警？",
    ]
    for question in questions:
        print("\nQUESTION:", question)
        vector = service.search(question, 6)
        bm25 = service.bm25_service.search(question, 6)
        hybrid = reciprocal_rank_fusion([vector, bm25])[:3]
        show("VECTOR TOP 6", vector, canonical)
        show("BM25 TOP 6", bm25, canonical)
        show("RRF TOP 3", hybrid, canonical)
    print("\nIDENTITY CHECKS PASSED")


if __name__ == "__main__":
    main()
