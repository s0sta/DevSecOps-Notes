---
id: p366
title: "Lakehouse governance, drawn"
slug: lakehouse-governance-drawn
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, Lakehouse, DataGovernance, ApacheIceberg, Analytics]
source: "LinkedIn post P366 · Data series"
linkedin_date: 2029-01-28
design: architecture
---

# Lakehouse governance, drawn

Three teams wrote to the same bucket, and the only map was a wiki page from 2023. When the revenue model broke, the fix took three days because nobody could say what fed it.

## Quick reference

- **Sources:** OLTP database (DB) · File drops (FILES) · Change streams (CDC)
- **Lake:** Raw zone (RAW) · Curated zone (CUR) · Table format (TBL)
- **Governance:** Catalogue (CAT) · Lineage (LINE) · Access policies (POL)

**Request flow:** OLTP database → Raw zone → Curated zone → Table format; Curated zone → Catalogue; Curated zone → Lineage; Curated zone → Access policies; File drops → Raw zone; Change streams → Raw zone

## Explained

### Sources

The OLTP database holds the current state of orders. File drops arrive from partners as CSV, on their schedule. Change streams read the database log and emit every insert and update as an event. All three land in the raw zone untouched, because the first rule of a lake is that you can replay it.

### Lake

The raw zone is immutable and cheap. The curated zone is where deduplication, typing and joins happen, and where the table format earns its keep: Iceberg, Delta or Hudi keeps a transaction log, so a reader sees a consistent snapshot while a writer adds files. The catalogue registers each table, so an engine finds it without a path.

### Governance

The catalogue holds names, schemas and owners. Lineage records which table and which column fed which, so an incident review becomes a walk downstream instead of a search. Access policies add row filters and column masks, so an analyst sees the region they own and not the national margin.

> **The honest caveat:** policies are enforced by the engine that reads the table. A role with direct access to the bucket can read the files and skip every mask, which is why the storage credentials matter as much as the policy.

> **The lesson:** the lake is storage, and the catalogue is the contract.

## In one line

> **Storage is easy. The catalogue is not.** Raw and curated zones are storage; the catalogue makes them answerable.

**Check snapshots**

```sql
SELECT * FROM db.orders.snapshots
```
