"""Shared, deliberately simple rules; these scores are not semantic accuracy."""

import re
import unicodedata


EVALUATOR_VERSION = "keyword-abstention-v2"


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", "", text).replace("*", "").replace("`", "")


def keyword_match(answer: str, expected_keywords: list[str]) -> bool:
    normalized = normalize_text(answer)
    return bool(expected_keywords) and all(
        normalize_text(keyword) in normalized for keyword in expected_keywords
    )


def is_refusal(answer: str) -> bool:
    # Heuristic only: a refusal followed by invented facts still needs review.
    phrases = [
        "无法确定", "无法确认", "不知道", "没有相关资料",
        "没有相关信息", "没有检索到相关资料", "无法回答",
        "知识库中没有", "证据不足", "没有找到", "无法提供",
    ]
    return any(phrase in normalize_text(answer) for phrase in phrases)


def source_hit(sources: list[dict], expected_source: str | None) -> bool:
    if expected_source is None:
        return False
    return any(source.get("document_name") == expected_source for source in sources)


def evaluate_answer(item: dict, answer: str) -> bool:
    if item["answerable"]:
        return keyword_match(answer, item["expected_keywords"])
    return is_refusal(answer)


def summarize(results: list[dict]) -> dict:
    """Failed calls remain in overall denominators, and are also counted separately."""
    total = len(results)
    successful = [row for row in results if row.get("error") is None]
    unknown = [row for row in results if not row["answerable"]]
    retrieval_rows = [row for row in results if row.get("retrieval_hit") is not None]

    def rate(rows, key):
        return sum(bool(row.get(key)) for row in rows) / len(rows) if rows else None

    return {
        "total": total,
        "successful": len(successful),
        "failed": total - len(successful),
        "answer_accuracy": rate(results, "answer_correct"),
        "refusal_accuracy": rate(unknown, "answer_correct"),
        # Only successfully retrieved answerable questions have this field.
        "retrieval_hit_at_3_successful": rate(retrieval_rows, "retrieval_hit"),
        "retrieval_evaluated_count": len(retrieval_rows),
        "average_latency_successful": (
            sum(row["latency_seconds"] for row in successful) / len(successful)
            if successful else None
        ),
        "category_accuracy": {
            category: rate(
                [row for row in results if row["category"] == category],
                "answer_correct",
            )
            for category in sorted({row["category"] for row in results})
        },
    }
