---
id: p263
title: "RAG vs fine-tuning"
slug: rag-vs-fine-tuning
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [RAG, LLM, AIEngineering, MachineLearning, DevOps]
source: "LinkedIn post P263 · Platform series"
linkedin_date: 2028-06-01
design: compare
---

# RAG vs fine-tuning

Retrieval-augmented generation and fine-tuning both make a general model useful for your product, and teams argue about them as if one replaces the other. They change different things, at different costs.

## Quick reference

| | **RAG** | **FINE-TUNE** |
|:--|:--|:--|
| What changes | Prompt and context only | The model's weights |
| Data needed | Docs plus an index | Labelled examples |
| Freshness | Reindex, no retrain | Retrain to update |
| Cost | Retrieval plus tokens | Training plus hosting |
| Latency | One extra hop | No retrieval hop |
| Best for | Changing, cited facts | Tone, format, one task |

**RAG** (Retrieval at query time): Search an index, put the best chunks in the prompt, nothing else changes.

Example: `retrieve then prompt`

**FINE-TUNE** (Weights changed by training): Train on your examples, ship new weights, serve a model that behaves your way.

Example: `train, evaluate, deploy`

- RAG → reindex, no retrain.
- Fine-tune → retrain, then serve.

## Explained

### How they differ

RAG leaves the weights alone. At query time you embed the question, search an index, and put the best chunks in the prompt. The model still knows only what it was trained on; the answer is grounded in documents you control.

Fine-tuning changes the weights. You show the model hundreds or thousands of input-output pairs and it learns a pattern: a format, a tone, a narrow task. The knowledge is baked in, so updating it means training again.

### Where RAG wins

Freshness. Reindex a changed document and the next answer reflects it, with no retraining and no redeploy.  
Provenance. You can return the source chunk with the answer, which is what a reviewer asks for.  
Cost. Indexing is cheap next to a training run.

### Where fine-tuning wins

Latency. No retrieval hop and a shorter prompt, so the first token arrives sooner.  
Consistency. A small model tuned on your examples can match a much larger general model on one narrow task.  
Cost at volume. A tuned small model is often cheaper per request than a large model with a long context.

> **The honest caveat:** fine-tuning does not reliably add facts, and RAG cannot teach a new output format. Most teams that need both start with RAG, then fine-tune for shape.

> **The rule:** retrieve for knowledge, train for behaviour.

Context is cheaper than weights.
