---
id: p235
title: "6 numbers that set your monitoring"
slug: 6-numbers-that-set-your-monitoring
sections: [devsecops]
topic: "Observability & SRE"
tags: [Prometheus, SRE, Observability, Monitoring, DevOps]
source: "LinkedIn post P235 · Platform series"
linkedin_date: 2028-03-28
design: numbers
---

# 6 numbers that set your monitoring

Monitoring defaults are not opinions. Six numbers decide how fast you notice, how often you page, and how far back you can look.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **15s** | Scrape interval | A common target: four samples a minute, enough for rate(). | scrape |
| **5m** | Alert for: duration | A starting point that skips one bad scrape and still pages fast. | alert |
| **14.4x** | Burn rate that pages | 1h at 14.4x spends 2% of a 30-day budget. Pair it with 5m. | SLO |
| **15d** | Retention default | Local Prometheus blocks last 15 days unless you raise it. | storage |
| **p99** | Not the average | The slowest 1% complains; the mean hides them. | latency |
| **30d** | SLO window | A month of requests makes a 99.9% target measurable. | window |

## Explained

### Scrape

15s, the scrape interval. Many teams scrape every 15 seconds: four samples a minute, enough for rate() and small enough to catch a short spike. Prometheus's own default is one minute, which is slower than most symptom alerts want.

### Alert

5m, the for: duration. A starting point for symptom alerts: long enough to skip a single bad scrape, short enough that five minutes of pain still gets a response. It is a choice, not a default.

14.4x, the burn rate that pages. At a 30-day budget, burning 14.4 times the normal rate for one hour spends 2% of the budget. That is the multi-window alert from the SRE workbook, paired with a 5m short window.

### Retain and read

15d, the retention default. Prometheus keeps local blocks for 15 days unless you raise it. That covers most incident reviews; it does not cover a quarterly trend, which is what remote storage is for.

p99, not the average. The slowest 1% is who complains, and the mean hides them. Put the percentile on the dashboard and the average in the appendix.

30d, the SLO window. A month of requests makes a 99.9% target measurable and stops a quiet week from flattering the number.

> **The honest caveat:** none of these is universal. A 15s scrape is wrong for an hourly batch job, and 15 days of retention is useless if reviews happen quarterly.

> **The lesson:** pick the number that matches the user-visible threshold, then configure the tool.

## In one line

> **Pick the number, then the tool.** A default nobody measured is a rumour with a config file.

**Set it in code**

```bash
scrape_interval: 15s
```
