# Day 4 - Document Parsing and Chunking

## Completed

- TXT parsing
- Markdown parsing
- PDF parsing
- Text cleaning
- Fixed-size chunking
- Paragraph-aware chunking
- Markdown-aware chunking
- Chunk metadata
- Document ingestion pipeline
- Chunk embedding

## Chunk Size

Large chunks:
- preserve more context
- consume more tokens
- may contain unrelated information

Small chunks:
- improve retrieval granularity
- may lose semantic context
- generate more vector records

## Chunk Overlap

Overlap preserves context near chunk boundaries.

Example:

chunk_size = 500
chunk_overlap = 100

Chunk 1:
0 - 500

Chunk 2:
400 - 900

## Different Data Types

TXT:
paragraph-aware chunking

Markdown:
heading → section → paragraph

PDF:
parse → clean → paragraph → fallback fixed-size

## Current Pipeline

Document
→ Parser
→ Text Cleaning
→ Chunking
→ Metadata
→ Embedding