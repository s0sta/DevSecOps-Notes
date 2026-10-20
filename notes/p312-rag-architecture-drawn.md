---
id: p312
title: "RAG architecture, drawn"
slug: rag-architecture-drawn
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [RAG, LLM, VectorDatabase, AIEngineering, SystemDesign]
source: "LinkedIn post P312 · Visual series"
linkedin_date: 2028-09-24
design: architecture
---

# RAG architecture, drawn

A RAG feature looks like one prompt and is really a pipeline. When the answer is wrong, the model is the last place to look.

## Quick reference

- **Tier 1 · Ingest:** Documents (DOCS) · Chunker (CHUNK) · Embeddings (EMBED)
- **Tier 2 · Store:** Vector index (VEC) · Metadata store (META)
- **Tier 3 · Serve:** API gateway (GW) · Retriever (TOPK) · Model (LLM)

**Request flow:** Documents → Chunker → Embeddings → Vector index → Retriever → Model; Metadata store → Retriever; API gateway → Retriever

**Around it:** Document store (RAW) · Embedding cache (CACHE) · Eval set (EVAL) · Access control (ACL)

## Explained

### Ingest

Documents arrive from a wiki, a share or a ticket queue. A parser turns them into text, a chunker cuts the text into overlapping passages, and an embedding model turns each passage into a vector. Chunk size is the first decision you will regret: too small and a passage loses its context, too large and the vector blurs several ideas into one.

### Store

The vectors go into a vector index that answers one question fast: which passages are closest to this query. Beside it sits a metadata store with source, owner, timestamp and access labels, because a vector without provenance cannot be cited or deleted.

### Serve

A request reaches the API gateway, which authenticates it and applies a quota. The retriever embeds the question, asks the index for the top passages, filters them by metadata, and passes them to the model. The citation is the only proof the answer has a source.

Around the tiers sit the parts that keep it honest: a document store for the originals, an embedding cache so the same text is not paid twice, an eval set that catches regressions, and access control on the passages each user may see.

> **The honest caveat:** no chunk size fixes a corpus that is out of date, and a high retrieval score is not confidence.

> **The lesson:** when RAG answers badly, read the retrieved chunks before you touch the prompt.

## In one line

> **RAG is a pipeline, not a prompt.** The model is the last box; everything before it decides what it sees.

**Check the chunks:** print the top 5 retrieved chunks
