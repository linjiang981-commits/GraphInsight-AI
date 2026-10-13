# Day8 Hybrid Retrieval Experiment


## Experiment Goal

Compare Vector Retrieval RAG and Hybrid Retrieval RAG.


## Baseline

Vector RAG

Pipeline:

Question
↓
Embedding
↓
pgvector
↓
LLM


## Proposed Method

Hybrid Retrieval RAG

Pipeline:

Question

↓

Vector Retrieval + BM25 Retrieval

↓

Fusion

↓

LLM


## Result


|Method|Accuracy|Latency|
|-|-|-|
|Vector RAG|50%|2.245s|
|Hybrid RAG|50%|2.182s|


## Analysis

The current experiment shows no obvious accuracy improvement.

Possible reasons:

1. Evaluation dataset size is limited.
2. Fusion strategy needs further optimization.
3. Some errors come from generation stage rather than retrieval stage.


Future optimization:

- RRF fusion
- Reranker
- Better evaluation metrics
