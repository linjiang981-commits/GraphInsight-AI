from pathlib import Path

from app.services.ingestion_service import (
    IngestionService
)


service = IngestionService()


file_path = (
    Path(__file__).resolve()
    .parents[1]
    / "data"
    / "sample_docs"
    / "tcp_troubleshooting.txt"
)


chunks = service.ingest_with_embeddings(
    file_path=file_path,
    chunk_size=200,
    chunk_overlap=40
)


print(
    "Total chunks:",
    len(chunks)
)


print(
    "Embedding dimension:",
    len(chunks[0]["embedding"])
)


for chunk in chunks:

    print(
        "\n========================"
    )

    print(
        "Chunk ID:",
        chunk["chunk_id"]
    )

    print(
        "Chars:",
        chunk["char_count"]
    )

    print(
        "Strategy:",
        chunk["chunk_strategy"]
    )

    print(
        "Embedding dimension:",
        len(chunk["embedding"])
    )

    print(
        "\n",
        chunk["content"]
    )