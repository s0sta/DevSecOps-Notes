---
id: p356
title: "ETL and ELT, drawn"
slug: etl-and-elt-drawn
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, ETL, DataWarehouse, Analytics, SQL]
source: "LinkedIn post P356 · Data series"
linkedin_date: 2029-01-04
design: architecture
---

# ETL and ELT, drawn

A report says revenue is up 4 percent and the warehouse says it is flat. Both read the same source; one of them read it before the transform.

## Quick reference

- **Tier 1 · Sources:** OLTP database (OLTP) · SaaS APIs (API) · Files and logs (FILE)
- **Tier 2 · Pipeline:** Extract (EX) · Transform (TX) · Load (LD)
- **Tier 3 · Warehouse:** Warehouse (WH) · Data marts (MART) · BI and dashboards (BI)

**Request flow:** OLTP database → Extract → Transform → Load → Warehouse → Data marts → BI and dashboards; SaaS APIs → Extract; Files and logs → Extract

## Explained

**Sources**  
Three kinds of source feed the pipeline: an OLTP database that holds the orders, SaaS APIs that hold billing and the CRM, and files and logs that arrive from everywhere else. Extract reads each one in its own way, and that is already the hardest part.

**Pipeline**  
Extract pulls the rows into a staging area. Transform cleans, joins and aggregates them, and load writes the result into the warehouse. ETL runs the transform before the load, so the heavy work happens on a separate engine and only clean rows land in the warehouse.

ELT keeps the same boxes and moves the letter: extract loads the raw rows into the warehouse, and the transform runs there, in SQL, next to the data. The warehouse, the marts and the BI layer then read from those tables.

**Warehouse**  
The warehouse holds the modelled tables. The marts narrow them for one team or one question, and the BI layer is where a human finally sees a number.

> **The honest caveat:** ELT is not free. The transform now competes with every dashboard for warehouse compute, and the raw layer grows without a retention rule.

> **The lesson:** the order of the letters is a decision about where the work runs and who pays for it.

## In one line

> **Transform where the data lives.** The order of the letters decides what pays for the compute.

**Count the rows**

```sql
select count(*) from orders
```
