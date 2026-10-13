from app.services.retrieval_service import RetrievalService


service = RetrievalService()


results = service.hybrid_search(
    "HTTP502是什么",
    3
)


for result in results:

    print("===================")

    print(
        result
    )