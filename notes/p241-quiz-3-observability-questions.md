---
id: p241
title: "Quiz: 3 observability questions"
slug: quiz-3-observability-questions
sections: [devsecops]
topic: "Observability & SRE"
tags: [Observability, SRE, Prometheus, CloudNative, DevOps]
source: "LinkedIn post P241 · Platform series"
linkedin_date: 2028-04-11
design: quiz
---

# Quiz: 3 observability questions

Three questions separate a dashboard someone built once from alerting that survives an on-call week. Answer before the reveal, then check the rule that caught you.

## Quick reference

**Q1. What does for: 5m change about an alert rule?**

- a) It fires only after 5 minutes of truth
- b) It retries the query every 5 minutes
- c) It silences the alert for 5 minutes

> **Answer:** a) It fires only after 5 minutes of truth. The rule stays pending while the expression is true and only fires after the whole duration, so one spike never pages anyone.

**Q2. What does a high-cardinality label do to Prometheus?**

- a) Nothing, labels are free
- b) Multiplies series, memory and disk
- c) Compresses samples more tightly

> **Answer:** b) Multiplies series, memory and disk. Every unique label value is a new series. A user ID label can take one metric to millions of series and slow every query until it times out.

**Q3. Why page on p99 latency instead of the average?**

- a) The average hides the slow tail
- b) p99 is cheaper to compute
- c) The average ignores failed requests

> **Answer:** a) The average hides the slow tail. Most requests are fast, so the mean stays low while the slowest one in a hundred waits. The tail is where timeouts and users give up.

## Explained

### The delay

Question one: what does for: 5m change? The rule fires only after the expression has been true for five minutes. Prometheus holds it in pending, re-evaluates each interval, and moves it to firing when the duration is done, so one failed scrape sets nothing off.

### Cardinality

Question two: what does a high-cardinality label do? Every unique label value is a new series, and every series costs memory and index space. A user ID or request ID label can take a single metric to millions of series and slow every query that touches it.

### The tail

Question three: why page on p99 instead of the average? Because the average is dragged down by the majority of fast requests. If 99 requests take 100ms and one takes 10 seconds, the mean still looks fine while one user waited ten seconds. The tail is where timeouts and retries live.

> **The honest caveat:** p99 over a one-minute window is noisy, and a slow tail on a quiet endpoint may be one user. Pair it with a longer window and a minimum request rate, or you will chase noise.

> **The lesson:** a number you cannot explain is a number you cannot page on.

## In one line

> **Ask what the number hides.** Three answers that change how you build dashboards.

**Test your rules**

```bash
promtool test rules test.yml
```
