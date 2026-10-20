---
id: p237
title: "How a metric becomes an alert"
slug: how-a-metric-becomes-an-alert
sections: [devsecops]
topic: "Observability & SRE"
tags: [Prometheus, Alerting, SRE, DevOps, Observability]
source: "LinkedIn post P237 · Platform series"
linkedin_date: 2028-04-02
design: pipeline
---

# How a metric becomes an alert

The page lands at 03:12. By then the metric has been scraped, stored, evaluated, fired, grouped and routed, and any of those six stages can be the reason it is late.

## Quick reference

1. **Scrape** — Prometheus pulls /metrics on a schedule, 1m by default. · *pull, not push*
2. **Store** — Samples go to the TSDB, one series per label set. · *tsdb*
3. **Evaluate** — The rule engine runs the PromQL expression on a timer. · *1m default*
4. **Fire** — True for the whole for: duration, then the alert fires. · `pending/firing`
5. **Route and group** — Alertmanager dedupes, groups and routes by labels. · `group_by`
6. **Notify** — A receiver delivers it: Slack, email, PagerDuty, webhook. · *receiver*

## Explained

### The path

Each stage has its own clock and its own way to fail.  
Scrape. Prometheus pulls /metrics from each target on the scrape interval, one minute by default.  
Store. Every sample is appended to the TSDB under its full label set, and that set is the series identity.  
Evaluate. On each evaluation_interval, also one minute by default, the rule engine runs the expression in expr.  
Fire. When the expression returns a result for the whole for: duration, the alert moves from pending to firing.  
Route and group. Prometheus sends firing alerts to Alertmanager, which groups and routes them by label.  
Notify. The receiver delivers: Slack, email, PagerDuty or a webhook, and the text is whatever the annotation said.

### Four clocks

Four clocks run here: scrape, evaluation, for: and Alertmanager's group_wait, 30 seconds by default. Add them up and a page can sit two or three minutes behind the event while every part works. The first notification of an incident is the slowest, because Alertmanager is still collecting siblings.

> **The honest caveat:** no stage knows what the user feels. The rule can be green while checkout is broken.

> **The lesson:** when a page is late or noisy, find the stage, not the person.

## In one line

> **An alert is a pipeline, not a bang.** Six stages stand between the metric and the page.

**Watch it fire**

```bash
ALERTS{alertstate="firing"}
```
