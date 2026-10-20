---
id: p232
title: "9 PromQL queries for real incidents"
slug: 9-promql-queries-for-real-incidents
sections: [devsecops]
topic: "Observability & SRE"
tags: [Prometheus, PromQL, SRE, Observability, Kubernetes]
source: "LinkedIn post P232 · Platform series"
linkedin_date: 2028-03-21
design: terminal
---

# 9 PromQL queries for real incidents

An alert fires at 02:14. Before you open a dashboard, answer three questions in order: is traffic normal, is it failing, is it slow. Nine PromQL lines do that.

## Quick reference

### Is it traffic?

```promql
# per-series request rate, last 5 minutes
rate(http_reqs_total[5m])
# one number for the whole service
sum(rate(http_reqs_total[5m]))
# split by status. Spikes show up here
sum by (code) (rate(http_reqs_total[5m]))
```

### Is it failing?

```promql
# 5xx per second, the headline number
sum(rate(http_reqs_total{code=~"5.."}[5m]))
# errors in the last hour, for the note
increase(http_reqs_total{code=~"5.."}[1h])
# 2.1% failing, from a recording rule
job:http_error_ratio:rate5m
```

### Is it slow?

```promql
# p50: the typical request
histogram_quantile(.5,rate(lat_bucket[5m]))
# p95: what most users feel
histogram_quantile(.95,rate(lat_bucket[5m]))
# p99 above 1s. This is the page
histogram_quantile(.99,rate(lat_bucket[5m]))
```

## Explained

### Rate

`rate(http_reqs_total[5m])` gives requests per second for each series.  
`sum(rate(http_reqs_total[5m]))` collapses them into one number for the service.  
`sum by (code) (rate(http_reqs_total[5m]))` splits it by status, which is where a spike first shows. A flat line means traffic is not your problem.

### Errors

`sum(rate(http_reqs_total{code=~"5.."}[5m]))` is the 5xx rate per second. Compare it with the same hour last week.  
`increase(http_reqs_total{code=~"5.."}[1h])` is the count for the incident note. It is the number you paste into the incident channel.  
`job:http_error_ratio:rate5m` is the ratio from a recording rule: 0.021 is 2.1% failing.

### Latency

`histogram_quantile(.5,rate(lat_bucket[5m]))` is p50, the typical request. A 41ms p50 with a 1.2s p99 is a bimodal service.  
`histogram_quantile(.95,rate(lat_bucket[5m]))` is p95, what most users feel. If p95 moves, they feel it.  
`histogram_quantile(.99,rate(lat_bucket[5m]))` is p99, and the one that pages.

### The habit

The habit that matters: start with rate, then errors, then latency. It stops you tuning a slow endpoint that is simply receiving a traffic spike, and answers the three questions in the order that matters. It is a triage order, not a tour of the metrics.

> **The honest caveat:** rate() needs a counter and at least two samples. A 5m window holds 20 scrapes at a 15s interval, so do not shorten it below a minute.

## In one line

> **Ask the metric, not the dashboard.** Every incident starts with one query and a timestamp.

**Try it**

```bash
promtool query instant http://localhost:9090 up
```
