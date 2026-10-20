---
id: p361
title: "Quiz: 3 pipeline questions"
slug: quiz-3-pipeline-questions
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, Kafka, DataPipelines, DataQuality, Analytics]
source: "LinkedIn post P361 · Data series"
linkedin_date: 2029-01-16
design: quiz
---

# Quiz: 3 pipeline questions

Three questions separate a pipeline you can operate from one you can only restart and hope.

## Quick reference

**Q1. Why must a consumer's write be idempotent before it retries?**

- a) Kafka can deliver the same record twice
- b) The broker rewrites records on retry
- c) Offsets are never committed twice

> **Answer:** a) Kafka can deliver the same record twice. At-least-once means a crash after the write and before the offset commit replays the record. An upsert keyed by the event id makes the replay harmless.

**Q2. What does a schema registry actually prevent?**

- a) A producer shipping a breaking change
- b) A topic running out of disk space
- c) A consumer reading too slowly

> **Answer:** a) A producer shipping a breaking change. It stores the schema per subject and checks each new version against a compatibility rule. A change compatible in shape but wrong in meaning still gets through.

**Q3. Why does a backfill need replayable history?**

- a) To rebuild a range without double counting
- b) Because storage is cheaper than compute
- c) So the dashboard refreshes faster

> **Answer:** a) To rebuild a range without double counting. A backfill re-reads the past. If the pipeline overwrote those rows, the input is gone; an append-only or partitioned history lets you recompute and swap.

## Explained

**Why idempotent writes**  
Question one: a consumer retries a batch after a crash. At-least-once delivery means the record written before the crash arrives again, so the write must be safe to repeat. An upsert on a natural key, or an insert that ignores a duplicate event id, makes the replay a no-op instead of a second charge.

**What a registry prevents**  
Question two: a producer ships a field rename, a type change or a removed column. The registry stores the schema per subject and checks the new version against a compatibility rule before the consumer sees it. It cannot stop a change that is structurally compatible but semantically wrong, such as a currency field that switches from cents to dollars.

**Why backfills need history**  
Question three: a bug corrupts ninety days of a derived table. If the pipeline overwrote rows in place, the input for those days is gone with them. With an append-only raw layer or partitioned history, you can recompute the range and swap it in, because the past still exists.

> **The honest caveat:** replay is only as good as the code that wrote the history. A raw table with no schema and no partition key is a pile of files, not a replayable log.

> **The lesson:** the pipeline is only as good as what it can rebuild.

## In one line

> **Replay decides what you can fix.** Three answers that separate a pipeline from a script.

**Read the subject**

```bash
curl -s localhost:8081/subjects
```
