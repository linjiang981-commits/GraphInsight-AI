# Day8 Hybrid Retrieval Experiment

> Historical experiment: the 50% scores below came from the original evaluator,
> which marked correct abstentions as wrong and failed on whitespace/Markdown.
> The old hybrid implementation also mixed JSON document IDs with database chunk
> IDs. These numbers must not be used to conclude that the methods performed equally.
>
> Re-scoring the saved answers with the shared rules gives Vector 12/12 and
> Hybrid 10/12. This is **offline rescoring of old answers**, not evidence of
> improved retrieval or a new generation run. See
> `ai-service/data/evaluation/vector_vs_hybrid_rescored.json` and
> [the repair guide](day8-repair-guide.md). A fresh comparison now uses the same
> database corpus, RRF and one RagService prompt.


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
