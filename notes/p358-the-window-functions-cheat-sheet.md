---
id: p358
title: "The window functions cheat sheet"
slug: the-window-functions-cheat-sheet
sections: [devsecops]
topic: "Data engineering"
tags: [SQL, DataEngineering, Analytics, Databases, DataWarehouse]
source: "LinkedIn post P358 · Data series"
linkedin_date: 2029-01-09
design: cheatsheet
---

# The window functions cheat sheet

A running total that resets halfway down the report is the classic window function bug. The function was right; the frame was not.

## Quick reference

### Rank

```bash
row_number() over (order by ts)
rank() over (order by score desc)
dense_rank() over (order by score)
ntile(4) over (order by score)
```

### Aggregate

```bash
sum(amount) over (partition by uid)
avg(amount) over (partition by uid)
count(*) over (partition by uid)
max(ts) over (partition by uid)
```

### Offset

```bash
lag(ts, 1) over (order by ts)
lead(ts, 1) over (order by ts)
first_value(ts) over (order by ts)
last_value(ts) over (order by ts)
```

### Frame

```bash
sum(x) over (order by d)
sum(x) over (partition by g)
sum(x) over (order by d rows 6 preceding)
sum(x) over ()
```

## Explained

**Rank**  
row_number() numbers every row. rank() leaves a gap after a tie, and dense_rank() does not. ntile(4) splits the partition into quarters. All four need an order, and none of them collapse rows.

**Aggregate**  
sum(), avg(), count() and max() with an OVER clause keep every row and add the aggregate beside it. Partition by the customer and you get a per-customer total on each order line, without a join or a group by.

**Offset**  
lag() reads the previous row and lead() reads the next, both inside the window. first_value() and last_value() reach the edges of the frame, and last_value() is the one that surprises people.

**Frame**  
The frame decides which rows the function sees. `sum(x) over (order by d)` is a running total, partition by g gives the whole partition, and rows 6 preceding gives a seven-row window. With ORDER BY and no frame, the default is range unbounded preceding to current row, which is why last_value() returns the current row.

> **The honest caveat:** frame and null ordering differ between engines. Postgres and BigQuery disagree about where nulls sort, and a query that works on one warehouse can rank differently on another.

> **The lesson:** the OVER clause is a frame, and the frame is usually the answer.

## In one line

> **The frame is the query.** Most window bugs are a missing frame, not a missing function.

**Test the frame**

```sql
select sum(x) over (order by d) from t
```
