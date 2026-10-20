---
id: p359
title: "5 data pipeline mistakes and the fix for each"
slug: 5-data-pipeline-mistakes-and-the-fix-for-each
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, DataPipelines, ETL, DataQuality, Analytics]
source: "LinkedIn post P359 · Data series"
linkedin_date: 2029-01-11
design: dontdo
---

# 5 data pipeline mistakes and the fix for each

Every pipeline in the incident channel has the same five decisions behind it, and each one saved an afternoon when it was made.

## Quick reference

**1.** ❌ **Retries with no idempotency** — A retried batch inserts every row a second time.  
✅ **Write by key, upsert** — The second run overwrites the first instead of doubling it.

**2.** ❌ **No schema contract** — A renamed column breaks the dashboard at 2am.  
✅ **A registry or a typed table** — Producer and consumer agree on the shape before the load.

**3.** ❌ **Backfills break consumers** — Reprocessing old dates overwrites the live tables.  
✅ **Replay into a new partition** — Write history beside the live table, then swap it in.

**4.** ❌ **No freshness checks** — A stalled job looks exactly like a quiet day.  
✅ **Check the maximum timestamp** — A table that has not moved in an hour fails the run.

**5.** ❌ **Local timezones in the data** — The DST hour repeats or vanishes every year.  
✅ **Store UTC, render local** — One instant on disk, one timezone at the edge.

## Explained

### The five

1. **Retries with no idempotency.** A batch fails halfway, the scheduler retries it, and every row that already landed lands again. Write by key with an upsert, so the second run overwrites the first instead of doubling it.

2. **No schema contract.** A producer renames a column, the load succeeds, and the dashboard breaks at 2am. A registry or a typed table catches the change at the producer, before it reaches the consumer.

3. **Backfills that break consumers.** Reprocessing last month in place overwrites the table the live dashboard reads. Write history into a new partition, check it, then swap it in.

4. **No freshness check.** A stalled job looks exactly like a quiet day: the table is there, the rows are old, and nobody notices. Fail the run when the maximum timestamp has not moved.

5. **Local timezones in the data.** Store the instant in UTC and render it in the user's zone. A timestamp with no zone is a timestamp with two meanings.

### What they share

Each one is a decision about the contract between two teams, which is why no single job's tests catch it.

> **The honest caveat:** an idempotent write still needs a key you trust. A natural key that changes, such as an email address, turns an upsert into a duplicate.

> **The lesson:** the pipeline is the contract, and every shortcut rewrites it without telling the other side.

## In one line

> **The pipeline is the contract.** Every shortcut rewrites it without telling the other side.

**Check the clock**

```sql
select max(updated_at) from orders
```
