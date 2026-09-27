from app.services.retrieval_service import (
    RetrievalService
)


retriever = RetrievalService()


query = (
   "为什么服务器无法建立新的连接？"
)


results = retriever.search(
    query=query,
    top_k=3
)


print(
    "\nQuery:",
    query
)

print(
    "\nTop Results:\n"
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
        result["content"]
    )

    print()