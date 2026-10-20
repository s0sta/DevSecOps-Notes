---
id: p357
title: "The lakehouse layers, drawn"
slug: the-lakehouse-layers-drawn
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, Lakehouse, Databricks, DeltaLake, Analytics]
source: "LinkedIn post P357 · Data series"
linkedin_date: 2029-01-07
design: explainer
---

# The lakehouse layers, drawn

A dashboard says revenue is 4 percent up, finance says it is flat, and both are reading the lakehouse. The argument is not about the number; it is about which layer each query touched.

## Quick reference

### Bronze - raw

- The source rows, appended as they arrived
- Schema as it came, quirks included
- Never edited in place, only added to
- Replay starts here

### Silver - cleaned

- Typed, deduplicated and conformed
- One row per entity, keys enforced
- Joins and business rules applied once
- Where most of the work actually lives

### Gold - modelled

- Star schemas and wide tables
- Named for the business, not the source
- What BI and finance actually read
- Rebuilt from silver, never patched

### Catalogue and lineage

- Every table has an owner and a description
- Lineage shows what a dropped column breaks
- Freshness and row counts sit beside it
- Without it, gold is only a rumour

> **Note:** The layers are a contract: each one is rebuildable from the one below.

## Explained

**Bronze**  
Bronze is the raw copy: the source rows appended as they arrived, with the quirks, the duplicates and the string dates intact. Nothing is edited in place, only added to, which is what makes a replay possible.

**Silver**  
Silver is the cleaned layer: typed, deduplicated and conformed. One row per entity, keys enforced, the joins and business rules applied once instead of in every query. It is the layer most teams underestimate, because it is where the work lives.

**Gold**  
Gold is modelled for consumption: star schemas, wide tables and names a finance analyst recognises. It is rebuilt from silver rather than patched, so the definition of revenue lives in one place.

**Catalogue and lineage**  
The catalogue gives every table an owner, a description and a freshness timestamp. Lineage shows what a dropped column would break, and a table with neither is a table nobody will trust.

> **The honest caveat:** the medallion is a convention, not a product. Bronze grows forever unless something deletes it, and naming the layers adds no lineage by itself.

> **The lesson:** a layer is only real if it can be rebuilt from the one below it.

## In one line

> **Each layer earns the next one.** Bronze is cheap; silver is where the work is.

**Check the catalogue**

```sql
select * from information_schema.tables
```
