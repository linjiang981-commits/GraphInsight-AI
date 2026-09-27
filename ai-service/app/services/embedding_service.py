from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

    def encode(
        self,
        texts: list[str]
    ):

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )