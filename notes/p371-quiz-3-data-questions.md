---
id: p371
title: "Quiz: 3 data questions"
slug: quiz-3-data-questions
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, DataGovernance, SQL, Analytics, MachineLearning]
source: "LinkedIn post P371 · Data series"
linkedin_date: 2029-02-08
design: quiz
---

# Quiz: 3 data questions

The last post of this 50-part series, and the right place to stop: the data itself. Three questions. Answer before the reveal.

## Quick reference

**Q1. Why does a table of a million embeddings need a vector index?**

- a) A scan compares every vector per query
- b) The database cannot store floats without one
- c) Embeddings are only valid inside an index

> **Answer:** a) A scan compares every vector per query. Without an index every query compares the vector to every row, then sorts: a million calculations per request. HNSW or IVFFlat visits a small candidate set instead.

**Q2. What does lineage give an incident review?**

- a) The downstream tables and reports to fix
- b) The exact SQL error from the failed job
- c) A copy of the data before the bad load

> **Answer:** a) The downstream tables and reports to fix. Lineage turns 'which dashboards are wrong' into a graph walk: find the bad table, then everything downstream of it. That list is the blast radius.

**Q3. Why start PII discovery with the schema, not the values?**

- a) Names, types and owners are cheap to read
- b) Values are always encrypted at rest
- c) A sample of every row is fast enough

> **Answer:** a) Names, types and owners are cheap to read. The schema is small, complete and already owned. Scanning values is slower, misses encrypted columns and free text, and a sample can miss the one row that matters.

## Explained

### Question one

Why does a table of a million embeddings need a vector index? Without one, every query compares the query vector to every row, a million calculations and a sort, per request. HNSW or IVFFlat visits a small candidate set instead and trades recall for milliseconds. A full scan is correct, just too slow to search.

### Question two

What does lineage give an incident review? The list of everything downstream of the bad table, and usually the one upstream table that caused it. Without it the review is four teams comparing screenshots.

### Question three

Why start PII discovery with the schema rather than the data? Because names, types and owners are complete, cheap to read and already maintained. Scanning values is slower, misses encrypted columns and free text, and a sample can miss the one row that matters.

> **The honest caveat:** passing this quiz does not make a warehouse trustworthy; the tests, the lineage and a named owner do.

If you got these, you are reading the data, not the dashboard. That is the discipline.

That is the series. Fifty posts, from a query plan to a feature store, five phases, and ten Python scripts you can run today. Thank you for following along.

> **The lesson:** the number is only as good as the table behind it.

## In one line

> **Own the data, not the dashboard.** Fifty posts, one rule: the number is only as good as the table behind it.

**Rerun the check**

```bash
python3 data_quality.py rows.jsonl
```
