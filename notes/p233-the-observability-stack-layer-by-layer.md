---
id: p233
title: "The observability stack, layer by layer"
slug: the-observability-stack-layer-by-layer
sections: [devsecops]
topic: "Observability & SRE"
tags: [Observability, Prometheus, SRE, OpenTelemetry, DevOps]
source: "LinkedIn post P233 · Platform series"
linkedin_date: 2028-03-23
design: stack
---

# The observability stack, layer by layer

Most monitoring stacks are drawn as boxes, which hides the only question that matters during an incident: where did the signal stop?

## Quick reference

*Bottom to top*

1. **Collection** — node_exporter, kubelet and app /metrics expose the raw numbers. · *agents*
2. **Pipeline** — The OpenTelemetry Collector batches, retries, samples and relabels. · *OTel Collector*
3. **Storage** — Prometheus writes 2-hour blocks; Thanos or Mimir keeps history. · *TSDB*
4. **Query** — PromQL reads the TSDB; Grafana draws it, but the query is the truth. · *PromQL*
5. **Alerting** — Alertmanager deduplicates, inhibits and routes to the right channel. · *Alertmanager*
6. **Action** — A runbook, a dashboard link and a rollback command, not just a page. · *runbooks*

## Explained

### Collect

Collection. node_exporter reads the host, kubelet exposes pod and container metrics, and every serious app publishes its own /metrics endpoint. Collection is pull by default: Prometheus scrapes, so a dead target shows up as down instead of silently missing.  
Pipeline. The OpenTelemetry Collector sits between the app and the store. It batches, retries, samples and relabels, and turns many formats into one. Useful, and one more thing to monitor.

### Store and query

Storage. Prometheus writes two-hour blocks into a local TSDB. That is fine for weeks, not years, so Thanos or Mimir takes the long-term copy.  
Query. PromQL reads the TSDB. Grafana draws the result, but the query is the truth, and a dashboard is only one view of it.

### Alert and act

Alerting. Alertmanager deduplicates, inhibits and routes. It decides who is woken up, so its config deserves review like code.  
Action. A page needs a runbook, a dashboard link and a rollback command. Without those, the alert is just a notification.

> **The lesson:** each layer has one job, and a wrong alert usually means one layer lost or changed the signal.

> **The honest caveat:** every added layer is a new failure point. A Collector between the app and Prometheus can drop or delay metrics, so monitor the Collector itself.

## In one line

> **Follow the signal, not the diagram.** Every wrong alert is a layer that lost or changed the signal.

**Monitor the collector**

```bash
curl localhost:8888/metrics
```
