---
id: p379
title: "Security posture at a glance"
slug: security-posture-at-a-glance
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [DevSecOps, CyberSecurity, Metrics, RiskManagement, AppSec]
source: "LinkedIn post P379 · DevSecOps series"
linkedin_date: 2029-02-27
design: dashboard
---

# Security posture at a glance

A security dashboard with forty tiles is wallpaper. The quarterly conversation needs six numbers, and each one has to be able to change a decision.

## Quick reference

**Status:** This quarter

| Metric | Value | Note |
|:--|:--|:--|
| Critical open | **12** | of 214 open findings |
| Mean time to fix | **9 days** | critical: 3 days |
| Scan coverage | **94%%** | repos scanned in CI |
| Secrets found | **7** | all rotated, none live |
| Patch compliance | **88%%** | within 14 days |
| Risks accepted | **3** | reviewed this quarter |

## Explained

**Critical open and time to fix**  
Critical open: 12 of 214 open findings are critical. On its own that is a count; next to mean time to fix, 9 days overall and 3 for criticals, it becomes a rate. A backlog growing faster than the fix rate is the signal that matters.

**Coverage and secrets**  
Scan coverage: 94 percent of repos run a scan in CI. The missing 6 percent is where the next finding will come from. Secrets found: 7 this quarter, all rotated, none live. The number to watch is time to rotate, not the count.

**Compliance and acceptance**  
Patch compliance: 88 percent of hosts are inside the 14-day window. Risks accepted: 3, reviewed this quarter. Accepted is a decision, so it needs an owner and a review date; an expired acceptance is an open risk with better paperwork.

**Why six**  
The six mix three counts, one duration and two percentages. That mix stops the page becoming a single number that hides the rest.

> **The honest caveat:** every one of these numbers is defined by someone. If the definition changes between quarters, the trend is fiction.

> **The lesson:** a posture dashboard is a set of decisions waiting to be made, not a scoreboard.

## In one line

> **A dashboard is a question.** Six tiles are only useful if one of them changes a decision.

**Pick one metric:** critical open / all open
