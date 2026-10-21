---
id: p458
title: "The layers of incident response"
slug: the-layers-of-incident-response
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, IncidentResponse, Reliability, DevOps, OnCall]
source: "LinkedIn post P458 · DevOps series"
linkedin_date: 2029-08-30
design: stack
---

# The layers of incident response

An incident is not one event. It is a stack of six decisions, and each layer can be the one that turns a bad hour into a bad week.

## Quick reference

*Bottom to top: signal to learning*

1. **Signal** — An SLO burn, a failed check or a customer report reaches a person. · `SLO / SYNTH`
2. **Triage** — Severity, scope and an owner are decided, often in ten minutes. · `SEV / OWNER`
3. **Mitigate** — Stop the bleeding: roll back, fail over, turn the feature off. · *ROLLBACK*
4. **Resolve** — Service is stable, data is corrected, the queue is drained. · *STABLE*
5. **Review** — The timeline is read; causes are separated from triggers. · *REVIEW*
6. **Prevent** — Actions with owners and dates, merged as code. · *PREVENT*

## Explained

### Signal and triage

Signal. Something is wrong and a machine says so: an SLO burn, a failed synthetic check, a customer report. Its job is to be specific and to reach a person, not a dashboard.

Triage. Someone decides how bad it is and who owns it: severity, scope, a first hypothesis. This is where a wrong call costs the most time, and where a missing owner shows up first.

### Mitigate and resolve

Mitigate. Stop the bleeding before you understand the cause: roll back, fail over, turn the feature off. The goal is a working service, not a complete explanation.

Resolve. Service is stable, data is corrected, the queue is drained. This is where incidents quietly become week-long projects, so write the exit condition down.

### Review and prevent

Review. Within a few days the timeline is read, and causes are separated from triggers. No blame, but no vague conclusions either.

Prevent. Actions with owners and dates, merged as code. A review with no change to the system is a meeting with extra steps.

> **The honest caveat:** the layers are not a waterfall. Most incidents loop between mitigate and triage while the cause stays unknown, and that is normal.

> **The lesson:** move through the stack deliberately, and never skip the last layer.

## In one line

> **Signal, then learning.** An incident that changes nothing will happen again.

**Check the exit:** did a merge change a default?
