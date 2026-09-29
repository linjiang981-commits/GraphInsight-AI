from app.services.database_retrieval_service import (
    DatabaseRetrievalService
)


retriever = DatabaseRetrievalService()


queries = [
    "为什么服务器出现大量CLOSE_WAIT？",
    "502错误是什么意思？",
    "DNS解析失败会造成什么问题？",
    "高并发短连接为什么会产生大量TIME_WAIT？"
]


for query in queries:

    results = retriever.search(
        query=query,
        top_k=3
    )

    print(
        "\n======================================"
    )

    print(
        "Query:",
        query
    )

    print(
        "======================================\n"
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{index}. "
            f"score={result['score']:.4f}"
        )

        print(
            "Source:",
            result["metadata"].get(
                "document_name"
            )
        )

        print(
            "Chunk:",
            result["chunk_index"]
        )

        print(
            result["content"]
        )

        print()