---
id: p418
title: "Security operations at a glance"
slug: security-operations-at-a-glance
sections: [devsecops]
topic: "Incident response & detection"
tags: [SecurityOperations, SOC, DevSecOps, CyberSecurity, SRE]
source: "LinkedIn post P418 · DevSecOps series"
linkedin_date: 2029-05-29
design: dashboard
---

# Security operations at a glance

The weekly review opened with a green dashboard and closed with two questions nobody could answer: how long did we take to notice, and how often were we wrong?

## Quick reference

**Status:** This week

| Metric | Value | Note |
|:--|:--|:--|
| Open incidents | **7** | 3 high or critical |
| MTTD | **18 min** | median, last 30 days |
| MTTR | **4h 10m** | alert to service restored |
| SLA breaches | **2** | one critical, overdue |
| Detections fired | **146** | this week, all rules |
| False positives | **21%%** | of 146 alerts |

## Explained

### The week

Open incidents: seven, three of them high or critical. A count is not a workload: two incidents with a named owner and a plan are lighter than seven nobody has touched.

MTTD: eighteen minutes, median over thirty days. Mean time to detect runs from the first event to the alert, so a rule with a one-hour window can never score below an hour.

MTTR: four hours ten minutes. Mean time to resolve runs from the alert to the service restored, and the definition is where meetings go wrong: resolve, respond and remediate are three different stop clocks.

SLA breaches: two, one critical and overdue. A breach is a finding about the process, not about the person who was on call when it landed.

### The signal

Detections fired: one hundred and forty-six this week, across every rule. The number says how much the programme produces; it says nothing about how much of it was true.

False positives: twenty-one percent of the 146 alerts. A fifth is tolerable if the queue stays short, and expensive if every one of those thirty-one alerts woke somebody.

> **The honest caveat:** a mean hides the tail. One twenty-six-hour incident disappears inside a four-hour average, so read the median and the ninetieth percentile too.

> **The lesson:** six numbers are a way to ask better questions, not the answer to the review.

## In one line

> **A dashboard is a starting point.** Six numbers open the review; they do not close it.

**Read the queue**

```bash
grep -c 'high' alerts.log
```
