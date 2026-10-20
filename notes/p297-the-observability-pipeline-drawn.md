---
id: p297
title: "The observability pipeline, drawn"
slug: the-observability-pipeline-drawn
sections: [devsecops]
topic: "Observability & SRE"
tags: [Observability, OpenTelemetry, Prometheus, SRE, DevOps]
source: "LinkedIn post P297 · Visual series"
linkedin_date: 2028-08-20
design: architecture
---

# The observability pipeline, drawn

An alert fires, the dashboard is green, and the trace nobody kept would have answered it in a minute. The observability pipeline is three tiers, and the signal can die in any of them.

## Quick reference

- **Signals:** App /metrics (APP) · node exporter (NODE) · kubelet (KUBE)
- **Pipeline:** OTel Collector (OTEL) · Prometheus (TSDB) · Loki (LOGS) · Tempo (TRACE)
- **Action:** Grafana (UI) · Alertmanager (PAGE)

**Request flow:** App /metrics → OTel Collector → Prometheus → Grafana; Prometheus → Alertmanager; node exporter → OTel Collector; kubelet → OTel Collector; Loki → Grafana; Tempo → Grafana

## Explained

### Signals

Signals come from three places. The app exposes /metrics on its own port, node exporter reports the host, and kubelet reports pods and containers. All three are pull endpoints, which is why a missing signal looks like a down target rather than silence. Each is scraped on a fixed interval, so the freshest number you have is always one scrape old.

### Pipeline

The pipeline starts at the OTel Collector, which receives every signal and batches it before the stores. Prometheus stores metrics, Loki stores logs, Tempo stores traces. Each keeps its own retention and query language, which is why one incident needs three different queries.

### Action

Action is Grafana and Alertmanager. Grafana queries all three and can put a trace ID next to the log line that explains it. Alertmanager takes what Prometheus fires, deduplicates, inhibits and routes it to a person.

> **The honest caveat:** sampling decides what you can answer later. A one percent trace sample keeps the shape of the tail, not the one request the customer rang about.

> **The lesson:** metrics say something is wrong, traces say where, logs say why. A pipeline that loses the link between them is three separate tools.

## In one line

> **Every signal has a leak.** The gap between a metric and a page is where incidents hide.

**Check the collector**

```bash
curl -s localhost:8888/metrics
```
