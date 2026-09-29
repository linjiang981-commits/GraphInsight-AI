# Day 5 - PostgreSQL and pgvector

## Completed

- Started PostgreSQL with Docker
- Enabled pgvector extension
- Created documents table
- Created document_chunks table
- Connected Python to PostgreSQL
- Persisted chunk embeddings
- Indexed multiple documents
- Implemented cosine vector search
- Implemented Top-K retrieval
- Verified Python process persistence
- Verified Docker volume persistence

## Architecture

Document
→ Parser
→ Chunk
→ Embedding
→ PostgreSQL + pgvector

Query
→ Embedding
→ Vector Search
→ Top-K Chunks

## PostgreSQL + pgvector

Current embedding dimension:

384

Database column:

VECTOR(384)

pgvector cosine distance operator:

<=>

Similarity score:

1 - cosine_distance

## Metadata

Metadata is stored using JSONB.

Example:

{
  "document_name": "network_guide.md",
  "document_type": ".md",
  "chunk_strategy": "markdown"
}

Metadata will later support:

- source citation
- knowledge-base filtering
- document filtering
- debugging

## Persistence

Python process restart:
data still exists.

Docker container restart:
data still exists because PostgreSQL uses Docker Volume.

## Current Limitation

The system currently retrieves Top-K chunks,
but does not yet send those chunks to the LLM.

Therefore the project currently has retrieval,
but not full RAG.

Day 6 will connect:

Retrieval
+
Context
+
LLM Generation