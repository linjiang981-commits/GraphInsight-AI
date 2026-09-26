import httpx


payload = {
    "messages": [
        {
            "role": "user",
            "content": "请简单介绍GraphRAG，控制在200字左右。"
        }
    ],
    "temperature": 0.3
}


with httpx.stream(
    "POST",
    "http://127.0.0.1:8000/api/chat/stream",
    json=payload,
    timeout=60.0,
    trust_env=False
) as response:

    print("Local FastAPI status:", response.status_code)

    if response.status_code != 200:

        body = response.read()

        print("Local FastAPI error body:")
        print(
            body.decode(
                "utf-8",
                errors="replace"
            )
        )

        raise SystemExit(1)

    print("\n开始接收流式数据：\n")

    for chunk in response.iter_text():

        print(
            chunk,
            end="",
            flush=True
        )

print("\n\n流式输出结束。")