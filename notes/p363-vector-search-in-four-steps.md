---
id: p363
title: "Vector search in four steps"
slug: vector-search-in-four-steps
sections: [devsecops]
topic: "Data engineering"
tags: [VectorSearch, Embeddings, AISearch, Postgres, MachineLearning]
source: "LinkedIn post P363 · Data series"
linkedin_date: 2029-01-21
design: explainer
---

# Vector search in four steps

A search box that returns the wrong five results usually has a good model and a bad second half. Most failures live in the last two steps.

## Quick reference

### Step 1 - Embed

- One model for documents and queries
- A 1,536-dimension float per row
- Normalise to make inner product cosine
- Re-embed everything when the model changes

### Step 2 - Index (HNSW)

- A multi-layer graph of near neighbours
- Search descends from a sparse top layer
- m=16 and ef_construction=64 by default
- ef_search trades recall for latency

### Step 3 - Similarity

- Cosine: 1 minus the distance, higher is closer
- Inner product arrives negated in pgvector
- L2 when magnitude should count
- Top k candidates, not final answers

### Step 4 - Rerank

- A cross-encoder rescores the top fifty
- Better ordering, milliseconds per batch
- Rerank only what the index returned
- Measure recall at k before and after

> **Note:** Brute force is exact and slow; every index is a promise about recall.

## Explained

### Embed

One model turns each document into a vector, and the query into one. A 1,536-dimension float per row is normal. If you rank by inner product, normalise both sides: inner product rewards a long vector as much as a similar one.

### Index

Comparing a query to every row is a full scan: fine at ten thousand rows, hopeless at ten million. HNSW builds a multi-layer graph, and the search descends from a sparse top layer into denser ones. The defaults are m=16 and ef_construction=64; ef_search, 40 by default, is the dial at query time.

### Similarity

Cosine distance, written <=>, is one minus cosine similarity, so lower is closer. Inner product, <#>, comes back negated so an ascending index scan works. L2, <->, is the plain distance. The index returns candidates, not answers, and returns them approximately.

### Rerank

A cross-encoder reads the query and each candidate together and rescores the top fifty. It costs milliseconds per batch and buys more accuracy than another index parameter. Rerank only what the index returned, and measure recall at k before and after.

> **The honest caveat:** every HNSW or IVFFlat index trades recall for speed, so the same query can return different rows than exact search. That is not a bug; it is a number you have to measure.

> **The lesson:** the index finds candidates, and the reranker decides the order.

## In one line

> **The index is an approximation.** Recall is a number you measure, not a promise the database makes.

**Tune the search**

```sql
SET hnsw.ef_search = 100;
```
