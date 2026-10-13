"""One evaluation path for LLM Only, Vector RAG and Hybrid RAG."""

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from app.services.evaluation_service import (
    EVALUATOR_VERSION, evaluate_answer, source_hit, summarize,
)


BASE = Path(__file__).resolve().parents[1]


def read_dataset(path: Path) -> list[dict]:
    dataset = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(dataset, list) or not dataset:
        raise ValueError("Evaluation dataset must be a non-empty list")
    ids = set()
    for item in dataset:
        for field in ["id", "category", "question", "answerable", "expected_keywords"]:
            if field not in item:
                raise ValueError(f"Missing evaluation field: {field}")
        if item["id"] in ids:
            raise ValueError(f"Duplicate question id: {item['id']}")
        ids.add(item["id"])
        if not isinstance(item["answerable"], bool):
            raise ValueError("answerable must be a boolean")
        if not isinstance(item["question"], str) or not item["question"].strip():
            raise ValueError("question must be non-empty text")
        keywords = item["expected_keywords"]
        if not isinstance(keywords, list) or not all(
            isinstance(word, str) and word.strip() for word in keywords
        ):
            raise ValueError("expected_keywords must be a list of non-empty strings")
        if item["answerable"] and (
            not keywords or not item.get("expected_source")
        ):
            raise ValueError("Answerable items need keywords and expected_source")
    return dataset


def fingerprint(value) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_evaluation(modes: list[str], output_prefix: str):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=BASE / "data/evaluation/rag_eval.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    dataset = read_dataset(args.dataset)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output = args.output or BASE / "data/evaluation" / f"{output_prefix}_{stamp}.json"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing evaluation: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    # Import/initialize live services only when executing, not on module import.
    from app.schemas.chat import ChatMessage
    from app.services.llm_service import LLMService

    llm = LLMService()
    rag = None
    corpus_before = None
    if any(mode != "llm_only" for mode in modes):
        from app.services.rag_service import RagService

        rag = RagService(llm_service=llm)
        corpus_before = rag.retriever.vector_store.list_chunks()
        if not corpus_before:
            raise ValueError("No database chunks; restore the corpus before evaluating")
        # Retrieval-only warmup; there is no paid LLM warmup call.
        for mode in modes:
            if mode == "vector":
                rag.retriever.search(dataset[0]["question"], top_k=3)
            elif mode == "hybrid":
                rag.retriever.hybrid_search(dataset[0]["question"], top_k=3)

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=BASE, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=BASE, text=True,
            stderr=subprocess.DEVNULL,
        ).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None

    report = {
        "run_type": "live_evaluation",
        "completed": False,
        "config": {
            "created_at_utc": stamp,
            "dataset_sha256": fingerprint(dataset),
            "corpus_sha256": fingerprint(corpus_before) if corpus_before is not None else None,
            "corpus_chunk_count": len(corpus_before) if corpus_before is not None else None,
            "corpus_unchanged": None,
            "git_commit": commit,
            "git_dirty": dirty,
            "model": llm.model,
            "embedding_model": (
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                if rag is not None else None
            ),
            "top_k": 3,
            "candidate_k": 6,
            "rrf_k": 60,
            "temperature": 0.1,
            "evaluator_version": EVALUATOR_VERSION,
            "prompt": "RagService.answer" if rag is not None else "LLMService + user question",
            "latency_scope": "retrieval + generation; excludes initialization and warmup",
        },
        "metrics": {},
        "results": [],
    }

    def save():
        report["metrics"] = {
            mode: summarize([row for row in report["results"] if row["mode"] == mode])
            for mode in modes
        }
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(output)

    # Reserve the output so another run cannot silently overwrite it.
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(f"Evaluating {len(dataset)} questions x {len(modes)} modes")
    print("Output:", output)
    for index, item in enumerate(dataset):
        # Alternate ordering to reduce systematic first/second-call latency bias.
        ordered_modes = modes if index % 2 == 0 else list(reversed(modes))
        for mode in ordered_modes:
            row = {
                "id": item["id"], "category": item["category"],
                "answerable": item["answerable"], "question": item["question"],
                "mode": mode, "answer": None, "sources": [],
                "answer_correct": False, "retrieval_hit": None,
                "error": None,
            }
            start = time.perf_counter()
            try:
                if mode == "llm_only":
                    answer = llm.chat(
                        messages=[ChatMessage(role="user", content=item["question"])],
                        temperature=0.1,
                    )
                    result = {"answer": answer, "sources": []}
                else:
                    result = rag.answer(
                        question=item["question"], top_k=3,
                        temperature=0.1, retrieval_mode=mode,
                    )
                row["latency_seconds"] = time.perf_counter() - start
                row["answer"] = result["answer"]
                row["sources"] = result["sources"]
                row["answer_correct"] = evaluate_answer(item, result["answer"])
                if mode != "llm_only" and item["answerable"]:
                    row["retrieval_hit"] = source_hit(
                        result["sources"], item["expected_source"]
                    )
            except Exception as exc:
                row["latency_seconds"] = time.perf_counter() - start
                row["error"] = type(exc).__name__
                print("Request failed:", item["id"], mode, row["error"])
            report["results"].append(row)
            save()
            print(item["id"], mode, "rule_correct=", row["answer_correct"])

    if rag is not None:
        corpus_after = rag.retriever.vector_store.list_chunks()
        report["config"]["corpus_unchanged"] = (
            fingerprint(corpus_before) == fingerprint(corpus_after)
        )
    report["completed"] = True
    save()
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    print("Saved:", output)
    if report["config"]["corpus_unchanged"] is False:
        raise SystemExit("Corpus changed during evaluation; this comparison is invalid")
    if any(row["error"] is not None for row in report["results"]):
        raise SystemExit("Some requests failed; inspect error counts in the report")
