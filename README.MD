# GraphInsight AI

GraphInsight AI is an enterprise intelligent knowledge
assistant based on RAG, GraphRAG and AI Agent.

## Architecture

- Frontend: Vue 3
- Business Backend: Spring Boot
- AI Service: FastAPI
- RAG: Coming soon
- GraphRAG: Coming soon
- Agent: Coming soon

## Current Progress

### Day 1

- [x] Initialize project structure
- [x] Build FastAPI service
- [x] Integrate LLM API
- [x] Build Spring Boot backend
- [x] Connect Spring Boot with FastAPI
- [ ] RAG
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

## Day 8 Authentication

- [x] PostgreSQL app_users persistence
- [x] BCrypt password hashing
- [x] JWT login and expiration
- [x] Bearer token validation
- [x] Protected AI endpoint
- [x] Current-user endpoint
- [x] Authentication integration tests

### API
POST /api/auth/login
GET /api/auth/me
POST /api/ai/chat

/api/auth/me requires a valid Bearer token.
/api/ai/chat also requires the ai:chat scope.

### Local setup
Start PostgreSQL and FastAPI.
Create backend-java/.env locally with the database credentials,
APP_JWT_SECRET, APP_DEMO_USERNAME, APP_DEMO_PASSWORD,
and APP_JWT_TTL_SECONDS. Never commit .env or tokens.

From backend-java:
.\start-dev.ps1

Tests:
.\mvnw.cmd test

This is a local learning implementation. FastAPI is an internal service.
Registration, refresh, revocation and production hardening are future work.

## Day 9 Knowledge Base Management

- Knowledge base CRUD with JWT-derived ownership.
- Per-user list/detail/update/delete authorization.
- Bounded pagination and ACTIVE/ARCHIVED status.
- Foreign-key relationships for document and conversation metadata.
- Empty knowledge bases can be deleted; non-empty deletion returns 409.
- Integration tests cover CRUD, isolation, validation and deletion constraints.

### APIs
- POST /api/knowledge-bases
- GET /api/knowledge-bases?page=0&size=10
- GET /api/knowledge-bases/{id}
- PUT /api/knowledge-bases/{id}
- DELETE /api/knowledge-bases/{id}

### Scope
Document upload, processing workers and message persistence are future work.
The existing Python RAG index is not yet scoped by knowledge base or user.

### Verification
Run from backend-java:
.\mvnw.cmd test

Complete the real PostgreSQL checks described in docs/day9-notes.md.