from app.services.chunking_service import (
    ChunkingService
)


text = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)


chunker = ChunkingService()


chunks = chunker.chunk_text(
    text=text,
    chunk_size=10,
    chunk_overlap=3
)


for index, chunk in enumerate(
    chunks,
    start=1
):

    print(
        index,
        chunk
    )