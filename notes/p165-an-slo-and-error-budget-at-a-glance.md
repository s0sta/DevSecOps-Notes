---
id: p165
title: "An SLO and error budget at a glance"
slug: an-slo-and-error-budget-at-a-glance
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, Observability, DevOps, CloudComputing, Reliability]
source: "LinkedIn post P165 · IT series"
linkedin_date: 2027-10-17
design: dashboard
---

# An SLO and error budget at a glance

An SLO turns "the service should be reliable" into a number, and an error budget turns that number into something you can actually manage. Here is how to read one.

## Quick reference

**Status:** This month, so far

| Metric | Value | Note |
|:--|:--|:--|
| SLO TARGET | **99.9%** | of requests succeed |
| Actual | **99.95%%** | better than target |
| Budget used | **45%** | of this month's allowance |
| Budget left | **24 min** | downtime you can still spend |
| Errors (30d) | **0.05%** | share of all requests |
| If spent | **freeze** | slow down risky releases |

## Explained

The SLO target: 99.9% of requests succeed. This is the promise. It sounds absolute, but the interesting part is the 0.1% that is allowed to fail.

The actual: 99.95% this month. Better than target, which means there is room to spare. Measuring the real number is the whole point; a target you do not measure is a wish.

Budget used: 45%. The error budget is the allowed failure, the 0.1%. Over a 30-day month, 99.9% allows about 43 minutes of downtime. Using 45% of it means you have spent roughly 20 of those minutes.

Budget left: 24 minutes. This is the key idea. Reliability is not "never fail", it is a budget you can spend. While budget remains, you can ship bold changes, run risky migrations, do chaos testing. The budget existing is permission to move fast.

Errors over 30 days: 0.05%. Comfortably inside the 0.1% allowance.

If spent: freeze. When the budget runs out, the policy kicks in: slow down, stop risky releases, and focus on reliability until the next window. This is what makes an SLO a decision tool, not just a dashboard number.

The maths: error budget = (1 - SLO) times total requests, or expressed as allowed downtime over the period.

Reliability is a budget. Spend it wisely.

## In one line

> **Reliability is a budget.** Spend it on bold releases while there is room; slow down when it runs low.

**The math:** budget = (1 - SLO) x total requests
