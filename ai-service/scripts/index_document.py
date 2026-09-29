from pathlib import Path

from app.services.ingestion_service import (
    IngestionService
)

from app.services.vector_store import (
    VectorStore
)


ingestion = IngestionService()

vector_store = VectorStore()


file_path = (
    Path(__file__).resolve()
    .parents[1]
    / "data"
    / "sample_docs"
    / "network_guide.md"
)


print(
    "Indexing:",
    file_path.name
)


chunks = (
    ingestion.ingest_with_embeddings(
        file_path=file_path,
        chunk_size=200,
        chunk_overlap=40
    )
)


document_id = (
    vector_store.create_document(
        file_name=file_path.name,
        file_type=file_path.suffix
    )
)


vector_store.add_chunks(
    document_id=document_id,
    chunks=chunks
)


print(
    "Document ID:",
    document_id
)

print(
    "Chunks inserted:",
    len(chunks)
)