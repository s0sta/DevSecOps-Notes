---
id: p353
title: "Kafka delivery semantics, drawn"
slug: kafka-delivery-semantics-drawn
sections: [devsecops]
topic: "Data engineering"
tags: [Kafka, DataEngineering, Streaming, DistributedSystems, Backend]
source: "LinkedIn post P353 · Data series"
linkedin_date: 2028-12-28
design: explainer
---

# Kafka delivery semantics, drawn

An invoice is charged twice after a consumer restarts mid-batch, and the review asks which delivery guarantee you chose. Kafka offers three, and none of them is free.

## Quick reference

### At-most-once

- Commit the offset before the work
- A crash loses the record, never repeats it
- Fine for metrics and sampled events
- No retry, no dedupe, no ceremony

### At-least-once

- Commit the offset after the work succeeds
- A crash repeats the last batch
- The shape of most consumers
- So the write has to be idempotent

### Exactly-once

- Idempotent producer plus transactions
- Offsets and output commit together
- Consumers read with read_committed
- Kafka Streams: exactly_once_v2

### Ordering per partition

- One partition is one ordered log
- The key picks the partition, every time
- More partitions, more parallel readers
- No order across two partitions

> **Note:** At-least-once plus an idempotent write is the exactly-once most teams need.

## Explained

**At-most-once**  
Commit the offset before the work. A crash between the commit and the write loses the record, and nothing retries it. It suits metrics and sampled events, where a missing point is cheaper than a duplicate.

**At-least-once**  
Commit after the work succeeds. A crash between the write and the commit replays the record, so the work runs twice. That is the shape of most consumers, and it is why the write must be idempotent: an insert keyed by the event id.

**Exactly-once**  
An idempotent producer removes duplicates from retries, and transactions commit offsets and output together. A consumer with read_committed sees only committed records, and Kafka Streams switches the whole pattern on with processing.guarantee=exactly_once_v2.

**Ordering per partition**  
One partition is one log with one reader order. The key chooses the partition, so every event for one order stays in order while different orders run in parallel. Across partitions there is no order at all.

> **The honest caveat:** exactly-once is a Kafka-to-Kafka promise. The moment the consumer writes to Postgres or S3, you are back to at-least-once plus your own idempotency.

> **The lesson:** the guarantee belongs to the whole path, not to the broker.

## In one line

> **Pick the guarantee before the code.** The setting is cheap; the missing dedupe is not.

**Read the config**

```bash
grep isolation.level consumer.properties
```
