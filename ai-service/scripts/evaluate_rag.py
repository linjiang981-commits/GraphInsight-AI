import json
import time
from pathlib import Path

from app.services.rag_service import RagService


eval_path = (
    Path(__file__).resolve()
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


rag = RagService()

def keyword_match(
    answer: str,
    expected_keywords: list[str]
) -> bool:

    if not expected_keywords:
        return False

    answer_lower = answer.lower()

    return all(
        keyword.lower() in answer_lower
        for keyword in expected_keywords
    )

def source_hit(
    sources: list[dict],
    expected_source: str | None
) -> bool:

    if expected_source is None:
        return False

    retrieved_sources = [
        source["document_name"]
        for source in sources
    ]

    return (
        expected_source
        in retrieved_sources
    )

def is_refusal(
    answer: str
) -> bool:

    refusal_phrases = [
        "无法确定",
        "没有相关资料",
        "无法回答",
        "知识库中没有",
        "证据不足"
    ]

    return any(
        phrase in answer
        for phrase in refusal_phrases
    )

results = []


for item in dataset:

    question = item["question"]

    print(
        "\n=============================="
    )

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
        question
    )


    start_time = time.perf_counter()


    result = rag.answer(
        question=question,
        top_k=3,
        temperature=0.1
    )


    latency = (
        time.perf_counter()
        - start_time
    )


    answer = result["answer"]

    sources = result["sources"]


    if item["answerable"]:

        answer_correct = keyword_match(
            answer,
            item[
                "expected_keywords"
            ]
        )

        retrieval_hit = source_hit(
            sources,
            item[
                "expected_source"
            ]
        )

        refusal_correct = False

    else:

        answer_correct = (
            is_refusal(answer)
        )

        retrieval_hit = False

        refusal_correct = (
            is_refusal(answer)
        )


    evaluation = {
        "id": item["id"],
        "category":
            item["category"],
        "question":
            question,
        "answer":
            answer,
        "answer_correct":
            answer_correct,
        "retrieval_hit":
            retrieval_hit,
        "refusal_correct":
            refusal_correct,
        "latency_seconds":
            round(latency, 3),
        "sources":
            sources
    }


    results.append(
        evaluation
    )


    print(
        "\nAnswer:"
    )

    print(answer)

    print(
        "\nAnswer Correct:",
        answer_correct
    )

    print(
        "Retrieval Hit:",
        retrieval_hit
    )

    print(
        "Latency:",
        round(latency, 3),
        "s"
    )

total = len(results)


answer_accuracy = (
    sum(
        1
        for result in results
        if result[
            "answer_correct"
        ]
    )
    / total
)


answerable_results = [
    result
    for result in results
    if not result["id"].startswith(
        "unknown_"
    )
]


retrieval_hit_rate = (
    sum(
        1
        for result in answerable_results
        if result[
            "retrieval_hit"
        ]
    )
    / len(answerable_results)
)


unknown_results = [
    result
    for result in results
    if result["id"].startswith(
        "unknown_"
    )
]


refusal_accuracy = (
    sum(
        1
        for result in unknown_results
        if result[
            "refusal_correct"
        ]
    )
    / len(unknown_results)
)


average_latency = (
    sum(
        result["latency_seconds"]
        for result in results
    )
    / total
)


print(
    "\n================================"
)

print(
    "FINAL EVALUATION"
)

print(
    "================================"
)

print(
    f"Answer Accuracy: "
    f"{answer_accuracy:.2%}"
)

print(
    f"Retrieval Hit@3: "
    f"{retrieval_hit_rate:.2%}"
)

print(
    f"Refusal Accuracy: "
    f"{refusal_accuracy:.2%}"
)

print(
    f"Average Latency: "
    f"{average_latency:.3f}s"
)

output_path = (
    Path(__file__).resolve()
    .parents[1]
    / "data"
    / "evaluation"
    / "rag_eval_results.json"
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

                "retrieval_hit_at_3":
                    retrieval_hit_rate,

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


print(
    "\nSaved to:",
    output_path
)