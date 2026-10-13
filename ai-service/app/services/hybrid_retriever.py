def reciprocal_rank_fusion(
    result_lists: list[list[dict]],
    rrf_k: int = 60,
) -> list[dict]:
    if rrf_k <= 0:
        raise ValueError("rrf_k must be positive")

    merged = {}
    for results in result_lists:
        seen = set()
        for rank, item in enumerate(results, start=1):
            chunk_id = item["id"]
            if chunk_id in merged:
                if merged[chunk_id]["content"] != item["content"]:
                    raise ValueError(f"Conflicting content for id={chunk_id}")
            if chunk_id in seen:
                continue
            seen.add(chunk_id)

            if chunk_id not in merged:
                merged[chunk_id] = {**item, "score": 0.0}
            merged[chunk_id]["score"] += 1.0 / (rrf_k + rank)

    return sorted(
        merged.values(),
        key=lambda item: (-item["score"], item["id"]),
    )
