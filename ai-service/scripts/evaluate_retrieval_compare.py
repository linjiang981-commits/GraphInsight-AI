import json
import time

from pathlib import Path


from app.services.database_retrieval_service import (
    DatabaseRetrievalService
)


from app.services.llm_service import (
    LLMService
)


from app.schemas.chat import (
    ChatMessage
)



# ===============================
# 加载测试集
# ===============================


eval_path = (

    Path(__file__)
    .resolve()
    .parents[1]

    /

    "data"

    /

    "evaluation"

    /

    "rag_eval.json"

)



with open(
    eval_path,
    "r",
    encoding="utf-8"
) as f:

    dataset = json.load(f)



# ===============================
# 初始化服务
# ===============================


retriever = DatabaseRetrievalService()

llm = LLMService()



# ===============================
# 简单评价
# ===============================


def keyword_match(
    answer,
    keywords
):


    if not keywords:

        return False


    for keyword in keywords:

        if keyword.lower() not in answer.lower():

            return False


    return True



# ===============================
# 执行RAG
# ===============================


def run_rag(
    mode,
    question
):


    if mode == "vector":

        results = (
            retriever.search(
                question,
                3
            )
        )


    else:

        results = (
            retriever.hybrid_search(
                question,
                3
            )
        )



    context = "\n\n".join(

        [
            item["content"]

            for item in results
        ]

    )


    prompt = f"""

请根据下面资料回答问题。

资料：

{context}


问题：

{question}

如果资料没有答案，请回答：
根据当前知识库无法确定。

"""



    messages=[

        ChatMessage(

            role="user",

            content=prompt

        )

    ]



    answer = llm.chat(

        messages,

        temperature=0.1

    )


    return answer, results




# ===============================
# Evaluation
# ===============================



final_results=[]



for item in dataset:


    print("\n====================")

    print(
        item["id"]
    )


    for mode in [
        "vector",
        "hybrid"
    ]:


        start=time.perf_counter()


        answer, sources = run_rag(

            mode,

            item["question"]

        )


        latency = (

            time.perf_counter()

            -

            start

        )



        correct = keyword_match(

            answer,

            item["expected_keywords"]

        )



        result={

            "id":
                item["id"],


            "mode":
                mode,


            "answer":
                answer,


            "correct":
                correct,


            "latency":
                round(
                    latency,
                    3
                ),


            "sources":

                [

                    s["id"]

                    for s in sources

                ]

        }



        final_results.append(
            result
        )


        print(
            mode,
            correct,
            latency
        )




# ===============================
# 统计
# ===============================


for mode in [

    "vector",

    "hybrid"

]:


    items=[

        x

        for x in final_results

        if x["mode"]==mode

    ]



    accuracy=(

        sum(

            x["correct"]

            for x in items

        )

        /

        len(items)

    )


    latency=(

        sum(

            x["latency"]

            for x in items

        )

        /

        len(items)

    )



    print("\n")

    print(
        mode
    )


    print(

        "Accuracy:",

        f"{accuracy:.2%}"

    )


    print(

        "Latency:",

        f"{latency:.3f}s"

    )



# 保存

output = (

    Path(__file__)
    .resolve()
    .parents[1]

    /

    "data"

    /

    "evaluation"

    /

    "vector_vs_hybrid.json"

)



with open(

    output,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        final_results,

        f,

        ensure_ascii=False,

        indent=2

    )


print(

    "saved:",

    output

)