# Day 2 - LLM Conversation

## Completed

- Multi-turn conversation messages
- System / User / Assistant roles
- Temperature configuration
- Token usage observation
- Context window concepts
- FastAPI streaming response
- Java ChatMessage / ChatRequest DTO upgrade
- Spring Boot → FastAPI multi-turn integration

## Key Concepts

### Multi-turn Conversation

LLM itself does not automatically remember previous HTTP requests.
Conversation history must be sent again through the messages array.

### Temperature

Lower temperature produces more stable responses.
Higher temperature increases diversity and randomness.

For enterprise RAG scenarios, lower values such as 0.1-0.3 are usually preferred.

### Context Window

System prompt, conversation history, retrieved context, user query
and model output all consume context space.

### Streaming

The model generates content incrementally and FastAPI forwards
the generated chunks to the client.

## Problems Encountered

HTTPX streaming test returned:

502 Bad Gateway

Cause:

The local HTTP request was affected by proxy environment settings.

Solution:

Use:

trust_env=False

when the test script accesses:

http://127.0.0.1:8000