from pathlib import Path

from app.services.document_parser import (
    DocumentParser
)

from app.services.chunking_service import (
    ChunkingService
)

from app.services.embedding_service import (
    EmbeddingService
)


class IngestionService:

    def __init__(self):

        self.parser = DocumentParser()

        self.chunker = ChunkingService()

        self.embedding_service = (
        EmbeddingService()
    )

    def ingest(
        self,
        file_path: str | Path,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> list[dict]:

        path = Path(file_path)

        text = self.parser.parse(path)

        if path.suffix.lower() == ".md":

            chunks = (
                self.chunker.chunk_markdown(
                    text,
                    chunk_size,
                    chunk_overlap
                )
            )

            strategy = "markdown"

        else:

            chunks = (
                self.chunker.chunk_by_paragraph(
                    text,
                    chunk_size,
                    chunk_overlap
                )
            )

            strategy = "paragraph"

        results = []

        for index, chunk in enumerate(chunks):

            results.append(
                {
                    "chunk_id": (
                        f"{path.stem}-{index}"
                    ),
                    "document_name": path.name,
                    "document_type": (
                        path.suffix.lower()
                    ),
                    "chunk_index": index,
                    "chunk_strategy": strategy,
                    "content": chunk,
                    "char_count": len(chunk)
                }
            )

        return results

    def ingest_with_embeddings(
        self,
        file_path: str | Path,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ) -> list[dict]:

        chunks = self.ingest(
            file_path,
            chunk_size,
            chunk_overlap
        )

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service.encode(
                texts
            )
        )

        for chunk, embedding in zip(
            chunks,
            embeddings
        ):

            chunk["embedding"] = (
                embedding.tolist()
            )

        return chunks