---
id: p238
title: "5 observability mistakes"
slug: 5-observability-mistakes
sections: [devsecops]
topic: "Observability & SRE"
tags: [Observability, SRE, Monitoring, DevOps, CloudNative]
source: "LinkedIn post P238 · Platform series"
linkedin_date: 2028-04-04
design: dontdo
---

# 5 observability mistakes

Every observability stack starts the same way: install Prometheus, add Grafana, feel modern. A year later the pager is noise and the bill is real, and the causes are almost always these five.

## Quick reference

**1.** ❌ **Alert on CPU above 80%** — CPU is a cause. Users feel latency and errors.  
✅ **Alert on latency and errors** — Those are the symptoms your SLO names.

**2.** ❌ **Dashboards nobody owns** — No owner means no one fixes it when it lies.  
✅ **One owner on every board** — A name in the title, checked each quarter.

**3.** ❌ **No SLO, only gut feel** — You cannot prioritise what you never defined.  
✅ **One SLO per user journey** — The error budget decides ship or fix.

**4.** ❌ **Log everything at debug** — Volume grows, signal does not, and the bill does.  
✅ **Info default, debug sampled** — Keep the fields you query, drop the rest.

**5.** ❌ **user_id as a metric label** — Every value is a new series, kept for ever.  
✅ **Labels from a bounded set** — Per-user detail belongs in logs and traces.

## Explained

### The five

1. **Alerting on CPU.** CPU at 80 percent is a cause, not a symptom; the symptom is a slow checkout. Page on latency and error rate, and keep CPU for diagnosis.
   \2. Unowned dashboards. A board with no owner stops being true and nobody notices for a quarter. Put a name in the title, or delete it.
   \3. No SLO. Without one, every alert is equally urgent and every priority argument is opinion. One SLO per user journey turns that into an error budget.
   \4. Logging everything. Debug lines multiply volume without adding signal, and the bill grows. Log at info, sample debug, and keep the fields you query.
   \5. High-cardinality labels. A user ID label creates a series per value, and Prometheus has to track every one. Put per-user detail in logs and traces.

### What they share

Each one buys a little short-term convenience and sends the bill to the person on call. None of them looks wrong on the day it is chosen.

> **The honest caveat:** an SLO is a negotiation, not a number you pick alone. Write it with the team that carries the pager.

> **The lesson:** observability is a budget, and every label spends from it.

## In one line

> **Observability is a budget.** Every label, log line and alert costs money and attention.

**Count your series**

```bash
count by (__name__) ({__name__=~".+"})
```
