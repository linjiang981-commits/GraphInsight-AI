# Day 6 - Naive RAG

## Completed

- Connected pgvector retrieval with LLM generation
- Built RAG prompt
- Added source citation
- Added structured source response
- Added /api/rag/query
- Tested private knowledge
- Tested out-of-knowledge questions
- Compared different Top-K values
- Compared different temperature values

## RAG

RAG =
Retrieval
+
Augmentation
+
Generation

## Pipeline

Question
→ Query Embedding
→ pgvector
→ Top-K Chunks
→ Build Context
→ RAG Prompt
→ LLM
→ Answer + Sources

## Grounding

The answer should be based on retrieved evidence.

RAG reduces hallucination but cannot completely eliminate it.

## Citation

Retrieved chunks are labeled:

[S1]
[S2]
[S3]

The LLM is instructed to cite these sources.

## Top-K

Small Top-K:
may miss useful information.

Large Top-K:
adds irrelevant context and token cost.

Top-K must be evaluated experimentally.

## Similarity Score

Vector similarity is NOT model confidence.

score = 0.8

does not mean:

80% probability that the answer is correct.

## Current System

LLM Only:
/api/chat

Retrieval Only:
/api/retrieval/search

RAG:
/api/rag/query