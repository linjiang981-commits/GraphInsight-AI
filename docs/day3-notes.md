# Day 3 - Embedding and Semantic Retrieval

## Completed

- Learned embedding concepts
- Implemented cosine similarity manually
- Used a real multilingual embedding model
- Built a 20-document network knowledge dataset
- Implemented semantic Top-K retrieval
- Added FastAPI retrieval endpoint

## Key Concepts

### Embedding

Embedding converts text into a high-dimensional numerical vector.

Semantically similar texts should have embeddings that are closer
in vector space.

### Cosine Similarity

Cosine similarity compares the direction of two vectors.

Higher similarity usually means the texts are semantically closer.

### Top-K Retrieval

The system ranks documents according to similarity and returns
the K most relevant documents.

### LLM vs Embedding

LLM:
generates text.

Embedding model:
generates vectors.

## Current Pipeline

Query
→ Embedding
→ Cosine Similarity
→ Ranking
→ Top-K Documents

This is retrieval, not full RAG yet.