# GraphInsight AI

GraphInsight AI is an enterprise intelligent knowledge
assistant based on RAG, GraphRAG and AI Agent.

## Architecture

- Frontend: Vue 3 (planned)
- Business Backend: Spring Boot
- AI Service: FastAPI
- RAG: Vector retrieval + BM25/RRF hybrid retrieval
- GraphRAG: Coming soon
- Agent: Coming soon

## Current Progress

### Day 1

- [x] Initialize project structure
- [x] Build FastAPI service
- [x] Integrate LLM API
- [x] Build Spring Boot backend
- [x] Connect Spring Boot with FastAPI
- [x] RAG (implemented after Day 1)
- [ ] GraphRAG
- [ ] Agent


## Current Features

- FastAPI AI service
- Spring Boot backend
- LLM chat
- Multi-turn context
- Streaming
- Document parsing
- Chunking
- Multilingual embeddings
- PostgreSQL + pgvector
- Vector retrieval
- Naive RAG
- Source citation
- Evaluation pipeline
- BM25 and vector retrieval over the same PostgreSQL chunks
- RRF fusion and selectable vector/hybrid RAG mode
- Shared evaluation rules and offline rescoring

## Day 8 repair and learning entry point

See [Day 8 repair guide](docs/day8-repair-guide.md) for the changed files,
startup checks, API examples and evaluation commands.

The original Day 8 result files are retained. Their historical 50% scores
included evaluation mistakes; offline rescoring is not a new model run.

## RAG Pipeline

Document
→ Parse
→ Chunk
→ Embed
→ pgvector

Question
→ Retrieve
→ Context
→ LLM
→ Answer + Sources
