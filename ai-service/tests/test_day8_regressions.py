import importlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient

from app.schemas.rag import RagRequest
from app.services.bm25_service import BM25Service, tokenize
from app.services.database_retrieval_service import DatabaseRetrievalService
from app.services.evaluation_service import evaluate_answer, keyword_match, summarize
from app.services.hybrid_retriever import reciprocal_rank_fusion
from app.services.rag_service import RagService
from scripts.rescore_evaluation import rescore


def chunk(chunk_id, content):
    return {
        "id": chunk_id, "document_id": 10, "chunk_index": chunk_id,
        "content": content,
        "metadata": {"document_name": "internal_network_policy.md"},
    }


class FakeEmbedding:
    def encode(self, texts):
        return np.array([[1.0, 0.0, 0.0] for _ in texts])


class FakeStore:
    def __init__(self):
        self.rows = [
            chunk(100, "GI-NET-017 DNS 缓存污染"),
            chunk(101, "GI-NET-023 API 网关上游连接超时"),
            chunk(102, "CLOSE_WAIT Socket 关闭"),
        ]

    def list_chunks(self):
        return self.rows

    def similarity_search(self, embedding, top_k):
        return [{**row, "score": 0.5} for row in self.rows[:top_k]]


class FakeLLM:
    model = "offline-test-model"

    def __init__(self):
        self.messages = []

    def chat(self, messages, temperature=0.1):
        self.messages.append(messages)
        return "API 网关上游连接超时。[S1]"

    async def stream_chat(self, messages, temperature=0.1):
        yield "offline"


class BM25Tests(unittest.TestCase):
    def test_identifier_tokens_and_case(self):
        self.assertEqual(tokenize("GI-NET-023 CLOSE_WAIT"), ["gi-net-023", "close_wait"])

    def test_metadata_survives_and_input_is_not_mutated(self):
        store = FakeStore()
        service = BM25Service()
        service.build_index(store.rows)
        result = service.search("gi-net-023")[0]
        self.assertEqual(result["id"], 101)
        self.assertEqual(result["metadata"], store.rows[1]["metadata"])
        self.assertNotIn("score", store.rows[1])

    def test_empty_and_unmatched_queries(self):
        service = BM25Service()
        service.build_index([])
        self.assertEqual(service.search("DNS"), [])
        service.build_index(FakeStore().rows)
        self.assertEqual(service.search("zzzz_unseen_token"), [])
        self.assertEqual(service.search("   "), [])
        with self.assertRaises(ValueError):
            service.search("DNS", top_k=0)

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            BM25Service().build_index([chunk(1, "A"), chunk(1, "B")])

    def test_common_term_not_discarded_just_for_nonpositive_score(self):
        service = BM25Service()
        service.build_index([chunk(1, "dns"), chunk(2, "dns")])
        self.assertEqual(len(service.search("dns")), 2)


class FusionTests(unittest.TestCase):
    def test_ranks_deduplication_and_metadata(self):
        a, b, c = chunk(1, "A"), chunk(2, "B"), chunk(3, "C")
        results = reciprocal_rank_fusion([[a, b], [b, c]])
        self.assertEqual([row["id"] for row in results], [2, 1, 3])
        self.assertTrue(math.isclose(results[0]["score"], 1 / 62 + 1 / 61))
        self.assertEqual(results[0]["metadata"], b["metadata"])
        self.assertNotIn("score", b)

    def test_duplicate_entry_counts_once_and_conflicts_fail(self):
        a = chunk(1, "A")
        self.assertEqual(reciprocal_rank_fusion([[a, a]])[0]["score"], 1 / 61)
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([[a], [chunk(1, "different")]])

    def test_empty_and_invalid_constant(self):
        self.assertEqual(reciprocal_rank_fusion([[], []]), [])
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([], rrf_k=0)


class RetrievalTests(unittest.TestCase):
    def test_database_id_space_and_refresh_after_ingestion(self):
        store = FakeStore()
        service = DatabaseRetrievalService(FakeEmbedding(), store)
        results = service.hybrid_search("GI-NET-023")
        self.assertEqual(results[0]["id"], 101)
        self.assertTrue(all(row["id"] >= 100 for row in results))
        store.rows.append(chunk(103, "GI-NET-099 special_case"))
        results = service.hybrid_search("GI-NET-099", top_k=4)
        self.assertIn(103, [row["id"] for row in results])
        self.assertEqual(service.hybrid_search(" "), [])

    def test_rag_modes_share_prompt_and_preserve_sources(self):
        store = FakeStore()
        retriever = DatabaseRetrievalService(FakeEmbedding(), store)
        llm = FakeLLM()
        rag = RagService(retriever, llm)
        for mode in ["vector", "hybrid"]:
            result = rag.answer("GI-NET-023", retrieval_mode=mode)
            self.assertTrue(result["sources"])
            self.assertEqual(result["sources"][0]["document_name"], "internal_network_policy.md")
            self.assertIn("id", result["sources"][0])
            self.assertIn("仅根据", llm.messages[-1][0].content)
        with self.assertRaises(ValueError):
            rag.answer("question", retrieval_mode="unknown")

    def test_no_evidence_does_not_call_llm(self):
        store = FakeStore()
        store.rows = []
        llm = FakeLLM()
        rag = RagService(DatabaseRetrievalService(FakeEmbedding(), store), llm)
        self.assertEqual(rag.answer("question", retrieval_mode="hybrid")["sources"], [])
        self.assertEqual(llm.messages, [])


class EvaluationTests(unittest.TestCase):
    def test_formatting_and_refusal(self):
        self.assertTrue(keyword_match("阈值为 **8 秒**。", ["8秒"]))
        self.assertTrue(keyword_match("API 网关上游连接超时。", ["API网关", "连接超时"]))
        self.assertFalse(keyword_match("当前没有答案", ["8秒"]))
        self.assertFalse(keyword_match("anything", []))
        self.assertTrue(evaluate_answer({"answerable": False}, "根据当前知识库无法确定。"))
        self.assertTrue(evaluate_answer({"answerable": False}, "我无法确认这家公司的总部地址。"))

    def test_failure_denominator_and_not_applicable_retrieval(self):
        rows = [
            {"category": "unanswerable", "answerable": False, "answer_correct": True,
             "retrieval_hit": None, "error": None, "latency_seconds": 1.0},
            {"category": "private_fact", "answerable": True, "answer_correct": False,
             "retrieval_hit": None, "error": "TimeoutError", "latency_seconds": 10.0},
        ]
        metrics = summarize(rows)
        self.assertEqual(metrics["failed"], 1)
        self.assertEqual(metrics["answer_accuracy"], 0.5)
        self.assertEqual(metrics["refusal_accuracy"], 1.0)
        self.assertIsNone(metrics["retrieval_hit_at_3_successful"])
        self.assertEqual(metrics["average_latency_successful"], 1.0)
        self.assertIsNone(summarize([])["answer_accuracy"])

    def test_rescore_preserves_old_result_and_no_stale_correct_key(self):
        item = {"id": "u1", "category": "unanswerable", "answerable": False}
        saved = [{"id": "u1", "mode": "hybrid", "answer": "无法确定", "correct": False, "latency": 1.0}]
        report = rescore(saved, [item])
        self.assertTrue(report["results"][0]["answer_correct"])
        self.assertFalse(report["results"][0]["previous_answer_correct"])
        self.assertNotIn("correct", report["results"][0])
        self.assertFalse(saved[0]["correct"])

    def test_runner_persists_errors_without_live_calls(self):
        from scripts.evaluation_runner import run_evaluation

        class FailingLLM(FakeLLM):
            def chat(self, messages, temperature=0.1):
                if messages[0].content == "fail":
                    raise TimeoutError("offline failure")
                return "无法确定"

        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory) / "dataset.json"
            output = Path(directory) / "result.json"
            dataset.write_text(json.dumps([
                {"id": str(index), "category": "unanswerable", "question": question,
                 "answerable": False, "expected_keywords": [], "expected_source": None}
                for index, question in enumerate(["ok", "fail"])
            ]), encoding="utf-8")
            args = ["test", "--dataset", str(dataset), "--output", str(output)]
            with patch.object(sys, "argv", args), patch(
                "app.services.llm_service.LLMService", FailingLLM
            ):
                with self.assertRaises(SystemExit):
                    run_evaluation(["llm_only"], "offline")
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertTrue(report["completed"])
                self.assertEqual(report["metrics"]["llm_only"]["failed"], 1)
                with self.assertRaises(FileExistsError):
                    run_evaluation(["llm_only"], "offline")


class APITests(unittest.TestCase):
    def test_schema_defaults_and_invalid_mode(self):
        self.assertEqual(RagRequest(question="DNS?").retrieval_mode, "vector")
        for payload in [
            {"question": " "},
            {"question": "DNS?", "retrieval_mode": "invalid"},
            {"question": "DNS?", "top_k": 0},
        ]:
            with self.assertRaises(ValueError):
                RagRequest(**payload)

    def test_app_startup_and_rag_contract(self):
        with patch("app.services.llm_service.LLMService", FakeLLM), patch(
            "app.services.database_retrieval_service.EmbeddingService", FakeEmbedding
        ):
            sys.modules.pop("app.main", None)
            module = importlib.import_module("app.main")
        module.rag_service.retriever.vector_store = FakeStore()
        with TestClient(module.app) as client:
            self.assertEqual(client.get("/health").status_code, 200)
            for mode in ["vector", "hybrid"]:
                response = client.post("/api/rag/query", json={
                    "question": "GI-NET-023", "retrieval_mode": mode,
                })
                self.assertEqual(response.status_code, 200, response.text)
                self.assertIn("id", response.json()["sources"][0])
                self.assertEqual(response.json()["sources"][0]["document_name"], "internal_network_policy.md")
            response = client.post("/api/rag/query", json={
                "question": "DNS?", "retrieval_mode": "invalid",
            })
            self.assertEqual(response.status_code, 422)
            response = client.post("/api/retrieval/search", json={"query": "DNS"})
            self.assertEqual(response.status_code, 200, response.text)
        sys.modules.pop("app.main", None)


if __name__ == "__main__":
    unittest.main()
