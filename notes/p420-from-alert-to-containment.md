---
id: p420
title: "From alert to containment"
slug: from-alert-to-containment
sections: [devsecops]
topic: "Incident response & detection"
tags: [IncidentResponse, DFIR, CyberSecurity, DevSecOps, SOC]
source: "LinkedIn post P420 · DevSecOps series"
linkedin_date: 2029-06-03
design: timeline
---

# From alert to containment

The alert arrived at 02:14. The credential was revoked at 02:39, and the review was written five days later. Between those two clocks sits the whole discipline.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **T+0** | Detected | The rule fires and the alert reaches the on-call queue. |
| **T+8m** | Triaged | Scope, severity and owner agreed in one thread. |
| **T+25m** | Contained | The credential is revoked and the host isolated. |
| **T+2h** | Eradicated | The entry point is closed and the implant removed. |
| **T+6h** | Recovered | Clean capacity serves traffic and the backlog drains. |
| **T+5d** | Reviewed | Timeline, cause and the control that changes. |

## Explained

### The first hour

Detected, T+0. The rule fires and the alert reaches the on-call queue. This is the only phase where the clock is not yours: the log latency, the rule window and the paging path decide how long it took.

Triaged, T+8m. Scope, severity and owner agreed in one thread. Triage answers three questions: what is affected, how bad is it, and who decides. Without an owner, the next four phases wait.

Contained, T+25m. The credential is revoked and the host isolated. Containment buys time and costs evidence: powering off loses volatile memory, so capture it first when the host matters.

### The next day

Eradicated, T+2h. The entry point is closed and the implant removed. If you skip this and go straight to recovery, the attacker returns through the same door.

Recovered, T+6h. Clean capacity serves traffic and the backlog drains. Recovery is a watched state: keep the heightened logging for a week, because the second attempt usually follows the first.

### The review

Reviewed, T+5d. Timeline, cause and the control that changes. The review is the only phase that improves the next incident, and it is the one that gets cancelled when the week is busy.

> **The honest caveat:** the phases overlap in practice. Containment starts before triage finishes, and recovery begins while eradication is still running.

> **The lesson:** speed in the first hour is bought by the runbook written last quarter.

## In one line

> **The clock does not stop at containment.** Six phases, and the last one is where the next incident is prevented.

**Time the phases**

```bash
date -u +%FT%TZ
```
