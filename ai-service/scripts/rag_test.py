from app.services.rag_service import (
    RagService
)


rag = RagService()


queries = [

    "为什么服务器出现大量CLOSE_WAIT？",

    "502 Bad Gateway 是什么意思？",

    "DNS解析失败会造成什么问题？"
]


for query in queries:

    print(
        "\n===================================="
    )

    print(
        "QUESTION:",
        query
    )

    print(
        "====================================\n"
    )


    result = rag.answer(
        question=query,
        top_k=3,
        temperature=0.2
    )


    print(
        "ANSWER:\n"
    )

    print(
        result["answer"]
    )


    print(
        "\nSOURCES:\n"
    )


    for source in result["sources"]:

        print(
            f"[S{source['rank']}] "
            f"{source['document_name']} "
            f"chunk={source['chunk_index']} "
            f"score={source['score']:.4f}"
        )