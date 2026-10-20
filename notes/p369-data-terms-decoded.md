---
id: p369
title: "Data terms, decoded"
slug: data-terms-decoded
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, CDC, Lakehouse, OLAP, DataGovernance]
source: "LinkedIn post P369 · Data series"
linkedin_date: 2029-02-04
design: reveal
---

# Data terms, decoded

Six words come up in every data meeting, and half the room nods at a different definition. Here is what each one buys and what it costs.

## Quick reference

- **CDC** — Change data capture: read the database log, not the table. Every change becomes an event, and the warehouse sees it in seconds.
- **ELT** — Extract, load, transform: land the raw data first, then transform it in SQL inside the warehouse. The raw copy stays replayable.
- **OLAP** — Online analytical processing: column stores that scan a few columns across billions of rows. Built for sums, not for one order by id.
- **Lakehouse** — Object storage plus an open table format (Iceberg, Delta or Hudi) plus a catalogue. Cheap like a lake, transactional like a warehouse.
- **Lineage** — The graph of which table and column fed which. It turns 'this report is wrong' into a list of downstream tables.
- **Cardinality** — How many distinct values a column holds. user_id is high, status is low, and the estimate decides join order.

## Explained

### CDC

Change data capture reads the database log, the WAL in Postgres or the binlog in MySQL, instead of polling the table. Every insert, update and delete becomes an event.

### ELT

Extract, load, transform. Land the raw data first, then transform it with SQL in the warehouse, so the raw copy stays replayable when the logic changes.

### OLAP

Online analytical processing: column stores built to scan a few columns across billions of rows. A sum over a month is fast; fetching one order by id is not.

### Lakehouse

Object storage plus an open table format (Iceberg, Delta or Hudi) plus a catalogue. Cheap like a lake, transactional like a warehouse.

### Lineage

The graph of which table and which column fed which. In an incident it names the upstream cause and everything downstream.

### Cardinality

The number of distinct values in a column. user_id is high, status is low, and the planner's estimate of both decides join order and index choice.

> **The honest caveat:** every one of these is a trade, and the bill arrives later. Replay costs storage, lineage costs instrumentation, and a lakehouse costs metadata discipline.

> **The lesson:** the words decide the design before the tool does.

## In one line

> **The words decide the design.** Each term is a cost you agree to when you pick the tool.

**Check cardinality**

```sql
SELECT count(DISTINCT country) FROM users
```
