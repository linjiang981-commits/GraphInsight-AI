# Day 7 - RAG Evaluation

## Key Concepts

### Ground Truth

Known correct answer used for evaluation.

### Baseline

A simple reference system used for comparison.

Current baseline:

LLM Only

Experiment:

Naive RAG

### Retrieval Hit@K

Whether the expected source appears in the Top-K retrieved results.

### Answer Accuracy

Whether the final answer contains the expected facts.

### Abstention

The model should explicitly state that the answer cannot be
determined when the knowledge base does not contain sufficient evidence.

### Error Analysis

Retrieval Error:
correct evidence was not retrieved.

Generation Error:
correct evidence was retrieved but the answer was incorrect.

Hallucination:
the knowledge base did not contain the answer but the model invented one.

Evaluation Error:
the answer was actually acceptable but the automatic metric judged it incorrectly.

## Evaluation Categories

- private_fact
- semantic_paraphrase
- unanswerable

## Comparison

LLM Only vs Naive RAG

Record real experimental results here.