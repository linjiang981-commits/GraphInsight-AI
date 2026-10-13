from app.services.bm25_service import BM25Service


docs = [

"HTTP 502 Bad Gateway通常表示网关或代理从上游服务器获得了无效响应。",

"HTTP 500表示服务器内部发生错误，需要检查服务端程序日志。",

"HTTP 404表示服务器没有找到请求对应的资源。"

]


bm25 = BM25Service()


bm25.build_index(
    docs
)


results = bm25.search(
    "HTTP502是什么",
    3
)


for r in results:

    print(r)