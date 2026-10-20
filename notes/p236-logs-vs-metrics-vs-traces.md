---
id: p236
title: "Logs vs metrics vs traces"
slug: logs-vs-metrics-vs-traces
sections: [devsecops]
topic: "Observability & SRE"
tags: [Observability, SRE, Prometheus, DevOps, Monitoring]
source: "LinkedIn post P236 · Platform series"
linkedin_date: 2028-03-30
design: compare
---

# Logs vs metrics vs traces

A page fires at 02:40 and checkout is slow. Three signals can explain it, and the team opens logs, as always.

## Quick reference

| | **METRICS** | **EVENTS** |
|:--|:--|:--|
| Answers | How much, how fast? | What happened, where? |
| Cost | Cheap per series | Per GB and per span |
| Cardinality | Bounded by labels | Unbounded by default |
| Best at | Trends and alerts | One request, end to end |
| Worst at | Explaining one request | Long-term trends |
| When to use | Always on | When you need detail |

**METRICS** (Numbers over time): Aggregates with labels: cheap, bounded, queried in milliseconds.

```promql
rate(http_requests_total[5m])
```

**EVENTS** (Logs and traces, one by one): Every event, kept for days: expensive per GB and per span.

```bash
{job="api"} |= "error"
```

- Metrics → keep them always, they are cheap.
- Logs + traces → open them when a page fires.

## Explained

### Three questions

Metrics answer how much and how fast: request rate, error ratio, p99 latency. Numbers with labels, cheap enough to keep for years.  
Logs answer what happened, in the words your code wrote: one line per event, with the fields you chose to print.  
Traces answer where the time went, span by span, across every service the request touched.

### Two families

The three split in two. Metrics are aggregates: one series per label set, and that set is the unit of cost. Logs and traces are events, priced per GB or per span.  
Cardinality is where the bill comes from: a user ID label turns one metric into millions of series and slows every query. Event data carries that detail by design, which is why it is sampled or kept for days.  
Metrics are best at trends and alerts, worst at explaining one request. Logs and traces are best at one request, and worst at cheap long-term trends.

### When to use each

Page on metrics, because they are always on. Open traces to find the slow hop, and logs to read the error in full.

> **The honest caveat:** traces are sampled at the SDK or the collector, so the slow request you hunt may not have been kept.

> **The lesson:** pick the signal by the question, not the tool you already have open.

## In one line

> **Metrics page. Events explain.** Metrics tell you something broke. Events tell you what.

**Add a trace:** trace_id in every log line
