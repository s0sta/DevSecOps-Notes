---
id: p409
title: "Application security at a glance"
slug: application-security-at-a-glance
sections: [devsecops]
topic: "Application & API security"
tags: [AppSec, DevSecOps, CyberSecurity, Metrics, RiskManagement]
source: "LinkedIn post P409 · DevSecOps series"
linkedin_date: 2029-05-08
design: dashboard
---

# Application security at a glance

A dashboard is not a security programme, but it is how you notice one. Six tiles, read left to right and top to bottom, answer the questions a lead asks on a Monday.

## Quick reference

**Status:** This sprint

| Metric | Value | Note |
|:--|:--|:--|
| Critical open | **7** | 2 past SLA |
| Authz failures | **3** | IDOR tests failing |
| WAF blocks | **12.4k** | last 24 hours |
| Dependency age | **148 d** | median, direct deps |
| Test coverage | **78%%** | authz and input tests |
| Open exceptions | **5** | 2 expire this month |

## Explained

### Findings

Critical open: seven, with two past their SLA. The age matters more than the count; a critical from last week is a decision, one from last quarter is a policy. Authz failures: three IDOR tests failing in the API suite. This is the number that predicts a breach, because a scanner rarely tests two accounts.

### Exposure

WAF blocks: 12.4k in the last day. A block is not a fix; a rising count can mean an attack, a noisy rule, or a scanner you own, so read the rule IDs before you celebrate.

### Debt

Dependency age: a median of 148 days for direct dependencies. Age is a proxy for missing patches, not risk on its own; a pinned library with no advisories is less urgent than a fresh one with a critical CVE.

### Assurance

Test coverage: 78 percent on the authz and input tests. Coverage proves a test exists, not that it asserts the right thing. Open exceptions: five accepted risks, two expiring this month. An exception without an expiry is a permanent hole with a ticket number.

> **The honest caveat:** every tile can improve while the product gets less safe. Fewer findings may mean better code or a scanner that stopped running, so plot the count against the scan volume.

> **The lesson:** a board is a prompt for questions, not an answer.

## In one line

> **Count what could hurt you.** Six numbers, and the one that should worry you.

**Export the board**

```bash
curl -s $API/metrics | jq .appsec
```
