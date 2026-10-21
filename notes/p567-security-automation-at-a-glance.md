---
id: p567
title: "Security automation at a glance"
slug: security-automation-at-a-glance
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, SecurityMetrics, Automation, SRE]
source: "LinkedIn post P567 · PythonSec series"
linkedin_date: 2030-05-12
design: dashboard
---

# Security automation at a glance

A monthly review opens with six tiles and a question: are the scripts doing anything useful? The tiles are not the answer, but each one can change the next decision.

## Quick reference

**Status:** Last 30 days

| Metric | Value | Note |
|:--|:--|:--|
| Scripts run | **1,284** | in 42 scheduled jobs |
| Findings open | **17** | 4 high, none critical |
| False positives | **9%%** | of 186 findings |
| Mean runtime | **38 s** | p95 is 2m 10s |
| Coverage | **91%%** | of 63 repos gated |
| Last failure | **2 days** | auth check, exit 2 |

## Explained

### What the six show

Scripts run: 1,284 across 42 scheduled jobs. A high count is activity, not coverage; 42 jobs that all scan the same repository would look busy and prove little.

Findings open: 17, four high and none critical. The shape matters more than the total, because a queue of lows with no owner is a backlog with better branding.

### The trust numbers

False positives: 9 percent of 186 findings. That is the trust metric. Every false positive spends a reviewer's attention, and attention is the scarce resource.

Mean runtime: 38 seconds, with a p95 of 2 minutes 10. The mean hides the tail, so read both before you decide a nightly job is cheap.

Coverage: 91 percent of 63 repositories are gated. The missing nine percent is where the next finding will come from.

Last failure: 2 days ago, an auth check that exited 2. A failure with an exit code is a fact; a failure without one is a rumour. The second kind is the one that wakes you up.

> **The honest caveat:** coverage counts repositories with a job, not repositories with a job that could fail. Check one gate by breaking it.

> **The lesson:** six numbers are questions, not a score.

## In one line

> **Six numbers, one question.** A dashboard opens the review; it does not close it.

**Read one tile**

```bash
grep -c 'exit 2' cron.log
```
