import json
import time
from pathlib import Path


from app.services.llm_service import LLMService
from app.schemas.chat import ChatMessage



# ==============================
# 1. 加载 Evaluation Dataset
# ==============================


eval_path = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "data"
    / "evaluation"
    / "rag_eval.json"
)


with open(
    eval_path,
    "r",
    encoding="utf-8"
) as file:

    dataset = json.load(file)



# ==============================
# 2. 初始化 LLM
# ==============================


llm = LLMService()



# ==============================
# 3. 关键词匹配评价
# ==============================


def keyword_match(
        answer: str,
        expected_keywords: list[str]
) -> bool:


    if not expected_keywords:

        return False


    answer_lower = answer.lower()


    for keyword in expected_keywords:

        if keyword.lower() not in answer_lower:

            return False


    return True




# ==============================
# 4. 无答案拒答检测
# ==============================


def is_refusal(
        answer: str
) -> bool:


    refusal_words = [

        "不知道",

        "无法确定",

        "没有相关信息",

        "无法回答",

        "知识库中没有",

        "没有找到",

        "无法提供"

    ]


    for word in refusal_words:

        if word in answer:

            return True


    return False





# ==============================
# 5. 开始 Evaluation
# ==============================


results = []



for item in dataset:


    print("\n============================")

    print(
        "ID:",
        item["id"]
    )

    print(
        "Category:",
        item["category"]
    )

    print(
        "Question:",
        item["question"]
    )


    start_time = time.perf_counter()



    # --------------------------
    # 调用普通 LLM
    # --------------------------


    messages = [

        ChatMessage(

            role="user",

            content=item["question"]

        )

    ]


    answer = llm.chat(

        messages=messages,

        temperature=0.1

    )



    latency = (
        time.perf_counter()
        -
        start_time
    )



    print("\nAnswer:")

    print(answer)



    # ==========================
    # Evaluation
    # ==========================


    if item["answerable"]:



        answer_correct = keyword_match(

            answer,

            item["expected_keywords"]

        )


        refusal_correct = False



    else:



        # 无答案问题

        answer_correct = is_refusal(

            answer

        )


        refusal_correct = answer_correct




    result = {


        "id":

            item["id"],



        "category":

            item["category"],



        "question":

            item["question"],



        "answer":

            answer,



        "answer_correct":

            answer_correct,



        "refusal_correct":

            refusal_correct,



        "latency_seconds":

            round(
                latency,
                3
            )

    }



    results.append(result)



    print(

        "Correct:",

        answer_correct

    )


    print(

        "Latency:",

        round(
            latency,
            3
        ),

        "s"

    )





# ==============================
# 6. 汇总指标
# ==============================


total = len(results)



answer_accuracy = (

    sum(

        1

        for r in results

        if r["answer_correct"]

    )

    /

    total

)



unknown_results = [

    r

    for r in results

    if r["id"].startswith(
        "unknown_"
    )

]



if len(unknown_results) > 0:


    refusal_accuracy = (

        sum(

            1

            for r in unknown_results

            if r["refusal_correct"]

        )

        /

        len(unknown_results)

    )


else:

    refusal_accuracy = 0




average_latency = (

    sum(

        r["latency_seconds"]

        for r in results

    )

    /

    total

)



# ==============================
# 7. 输出结果
# ==============================



print("\n================================")

print("LLM ONLY EVALUATION RESULT")

print("================================")



print(

    f"Answer Accuracy: "
    f"{answer_accuracy:.2%}"

)


print(

    f"Refusal Accuracy: "
    f"{refusal_accuracy:.2%}"

)



print(

    f"Average Latency: "
    f"{average_latency:.3f}s"

)





# ==============================
# 8. 保存结果
# ==============================



output_path = (

    Path(__file__)

    .resolve()

    .parents[1]

    /

    "data"

    /

    "evaluation"

    /

    "llm_only_results.json"

)



with open(

    output_path,

    "w",

    encoding="utf-8"

) as file:


    json.dump(

        {

            "metrics": {


                "answer_accuracy":

                    answer_accuracy,


                "refusal_accuracy":

                    refusal_accuracy,


                "average_latency":

                    average_latency


            },


            "results":

                results

        },


        file,

        ensure_ascii=False,

        indent=2

    )



print()

print(

    "Saved:",

    output_path

)