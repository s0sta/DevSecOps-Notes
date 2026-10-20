---
id: p367
title: "Data quality, four checks"
slug: data-quality-four-checks
sections: [devsecops]
topic: "Data engineering"
tags: [DataQuality, DataEngineering, Analytics, SQL, DataGovernance]
source: "LinkedIn post P367 · Data series"
linkedin_date: 2029-01-30
design: explainer
---

# Data quality, four checks

The pipeline was green, the dashboard loaded, and the revenue number was forty percent low. Nothing had failed. The data was simply incomplete.

## Quick reference

### Completeness

- Expected rows against rows landed
- Nulls in the columns that matter
- Counts per partition, not just the total
- A missing partition is a failed load

### Uniqueness

- One row per key, enforced by a test
- A duplicate doubles every sum after it
- Test the natural key, not the surrogate id
- Late data is the usual culprit

### Validity

- Types, ranges, enums and regex
- 1970-01-01 is a sentinel, not a birthday
- Reject at the edge, not in the report
- Null is not the same as zero

### Freshness

- The age of the newest partition
- A staleness SLA per table
- Alert on lag, not only on failure
- Fresh but wrong is still wrong

> **Note:** A check you did not write is a failure you will not see.

## Explained

### Completeness

Expected rows against rows landed, nulls in the columns that matter, and counts per partition rather than a total. A missing partition is the most common failure, and a healthy total can hide it, because the other partitions grew.

### Uniqueness

One row per key. A duplicate doubles every sum that follows, and the natural key is the one to test, not the surrogate id, which is unique by construction and tells you nothing.

### Validity

Types, ranges, enums and regular expressions. A date of 1970-01-01 is a sentinel, not a birthday, and a negative quantity is a refund or a bug. Reject at the edge, where the message can still name the source file.

### Freshness

The age of the newest partition, measured against a staleness SLA per table. Measure it from the newest event, not from the job's exit time. Alert on lag rather than on failure, because a job that succeeds and writes nothing is the failure that pages nobody.

> **The honest caveat:** these four checks test structure, not meaning. A currency conversion applied twice passes all of them, and so does a correct table joined to the wrong one.

> **The lesson:** test the data, not the job.

## In one line

> **Test the data, not the job.** A green pipeline can still write an empty table.

**Check freshness**

```sql
SELECT max(loaded_at) FROM orders
```
