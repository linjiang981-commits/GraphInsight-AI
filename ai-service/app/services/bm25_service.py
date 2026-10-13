import re
import unicodedata

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return re.findall(
        r"[a-z0-9]+(?:[-_][a-z0-9]+)*|[\u4e00-\u9fff]",
        normalized,
    )


class BM25Service:
    def __init__(self):
        self.documents = []
        self.token_sets = []
        self.bm25 = None

    def build_index(self, documents: list[dict]):
        ids = [item["id"] for item in documents]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate IDs in BM25 input")

        self.documents = [dict(item) for item in documents]
        corpus = [tokenize(item["content"]) for item in self.documents]
        self.token_sets = [set(tokens) for tokens in corpus]
        self.bm25 = BM25Okapi(corpus) if corpus and any(corpus) else None

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if top_k < 1:
            raise ValueError("top_k must be positive")

        tokens = tokenize(query)
        if self.bm25 is None or not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        query_terms = set(tokens)
        # 只要求存在词项交集，不把 score <= 0 当作普遍无关标准。
        indices = [
            index for index, terms in enumerate(self.token_sets)
            if query_terms & terms
        ]
        indices.sort(
            key=lambda index: (
                -float(scores[index]), self.documents[index]["id"]
            )
        )
        return [
            {**self.documents[index], "score": float(scores[index])}
            for index in indices[:top_k]
        ]
