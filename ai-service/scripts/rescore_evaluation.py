"""Re-score saved answers without database/model access or changing the original."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.services.evaluation_service import EVALUATOR_VERSION, evaluate_answer, summarize
from scripts.evaluation_runner import BASE, fingerprint, read_dataset


def rescore(raw, dataset: list[dict]) -> dict:
    rows = raw if isinstance(raw, list) else raw["results"]
    questions = {item["id"]: item for item in dataset}
    results = []
    for saved in rows:
        item = questions[saved["id"]]
        error = saved.get("error")
        answer = saved.get("answer")
        row = {
            **saved,
            "category": item["category"],
            "answerable": item["answerable"],
            "mode": saved.get("mode", "saved_answers"),
            "previous_answer_correct": saved.get("answer_correct", saved.get("correct")),
            "answer_correct": evaluate_answer(item, answer) if error is None and isinstance(answer, str) else False,
            "retrieval_hit": saved.get("retrieval_hit") if item["answerable"] else None,
            "latency_seconds": saved.get("latency_seconds", saved.get("latency", 0.0)),
            "error": error,
        }
        # Avoid retaining a stale contradictory score under the old key.
        row.pop("correct", None)
        row.pop("refusal_correct", None)
        results.append(row)
    modes = sorted({row["mode"] for row in results})
    return {
        "run_type": "rescore_saved_answers",
        "evaluator_version": EVALUATOR_VERSION,
        "dataset_sha256": fingerprint(dataset),
        "note": "No retrieval or generation rerun. Latencies and evidence are historical.",
        "metrics": {
            mode: summarize([row for row in results if row["mode"] == mode])
            for mode in modes
        },
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--dataset", type=Path, default=BASE / "data/evaluation/rag_eval.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    report = rescore(raw, read_dataset(args.dataset))
    report["source_file"] = args.input.name
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output = args.output or args.input.with_name(f"{args.input.stem}_rescored_{stamp}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    print("Saved:", output)


if __name__ == "__main__":
    main()
