---
id: p364
title: "The pgvector cheat sheet"
slug: the-pgvector-cheat-sheet
sections: [devsecops]
topic: "Data engineering"
tags: [Postgres, pgvector, VectorSearch, SQL, DataEngineering]
source: "LinkedIn post P364 · Data series"
linkedin_date: 2029-01-23
design: cheatsheet
---

# The pgvector cheat sheet

You have Postgres, you have embeddings, and no appetite for a second database. pgvector is one extension, one column type, two index types and four operators.

## Quick reference

### Setup

```sql
CREATE EXTENSION IF NOT EXISTS vector;
SELECT extversion FROM pg_extension;
\dx vector
SHOW server_version;
```

### Store

```sql
CREATE TABLE t (id int, v vector(3));
INSERT INTO t VALUES (1, '[1,2,3]');
SELECT id, v::text FROM t;
UPDATE t SET v = '[3,2,1]';
ALTER TABLE t ADD v2 vector(3);
```

### Index

```sql
CREATE INDEX ON t USING ivfflat (v);
CREATE INDEX ON t USING hnsw (v
  vector_l2_ops) WITH (m = 16);
SET hnsw.ef_search = 100;
SET ivfflat.probes = 10;
```

### Query

```sql
SELECT * FROM t ORDER BY v <-> $1 LIMIT 5
SELECT v <=> '[1,2,3]' AS cos FROM t;
SELECT v <#> '[1,2,3]' AS ip FROM t;
SELECT v <+> '[1,2,3]' AS l1 FROM t;
SELECT 1 - (v <=> $1) AS sim;
```

## Explained

### Setup

`CREATE EXTENSION IF NOT EXISTS vector;` runs once per database, not once per cluster. `SELECT extversion FROM pg_extension;` shows the version, `\dx vector` lists it in psql, and `SHOW server_version;` tells you what you run against.

### Store

The column is the schema. `CREATE TABLE t (id int, v vector(3));` pins the dimension, and `INSERT INTO t VALUES (1, '[1,2,3]');` takes a string Postgres casts for you. Read it with `SELECT id, v::text FROM t;` and update it with `UPDATE t SET v = '[3,2,1]';`.

### Index

ivfflat has a default operator class, so `CREATE INDEX ON t USING ivfflat (v);` works, and lists default to 100. HNSW has no default, so the statement wraps to name vector_l2_ops and m=16. At query time `SET hnsw.ef_search = 100;` and `SET ivfflat.probes = 10;` buy recall with latency.

### Query

`SELECT * FROM t ORDER BY v <-> $1 LIMIT 5` is the shape that uses an index: a distance operator in ORDER BY, ascending, with a LIMIT. The vector arrives as a bind parameter, which is why the sheet writes $1. The other lines show <=>, <#> and <+>.

> **The honest caveat:** the index is used only for that ORDER BY shape. Put the distance in a SELECT list, or sort descending, and you get a full scan instead.

> **The lesson:** the operator picks the metric, and the index only makes it fast.

## In one line

> **Store the vector, query the distance.** The operator picks the metric; the index only makes it fast.

**Show the plan**

```sql
EXPLAIN ANALYZE SELECT * FROM t
```
