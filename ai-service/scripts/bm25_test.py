from app.services.bm25_service import BM25Service, tokenize


def main():
    documents = [
        {"id": 1, "content": "GI-NET-017 表示 DNS 缓存污染排查流程。"},
        {"id": 2, "content": "GI-NET-023 表示 API 网关上游连接超时排查流程。"},
        {"id": 3, "content": "CLOSE_WAIT 通常与本地应用没有关闭 Socket 有关。"},
    ]
    service = BM25Service()
    service.build_index(documents)

    print("Tokens:", tokenize("GI-NET-023 CLOSE_WAIT"))
    results = service.search("GI-NET-023", top_k=3)
    for result in results:
        print(result)

    assert results and results[0]["id"] == 2
    assert service.search("zzzz_unseen_token") == []
    service.build_index([])
    assert service.search("DNS") == []
    print("BM25 CHECKS PASSED")


if __name__ == "__main__":
    main()
