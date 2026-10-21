---
id: p452
title: "The on-call system, drawn"
slug: the-on-call-system-drawn
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, OnCall, IncidentResponse, DevOps, Reliability]
source: "LinkedIn post P452 · DevOps series"
linkedin_date: 2029-08-16
design: architecture
---

# The on-call system, drawn

At 03:12 the pager goes off, and the person it reaches has the runbook open before the second alert lands. It is a system with three tiers, and each one answers a different question.

## Quick reference

- **Tier 1 · Signals:** SLO alert (SLO) · Synthetic check (SYNTH)
- **Tier 2 · Rotation:** Primary on-call (P1) · Secondary on-call (P2)
- **Tier 3 · Escalation:** Incident commander (IC) · Duty manager (MGR)

**Request flow:** SLO alert → Primary on-call → Incident commander; Primary on-call → Duty manager; Synthetic check → Primary on-call; Secondary on-call → Incident commander

**Around it:** Pager (PAGE) · Status page (STAT) · Incident channel (CHAT) · Runbook (RUN)

## Explained

### Signals

An SLO alert fires when the error budget is burning fast enough that a human should look now, not when one request fails. A synthetic check calls the login page from three regions every minute, so a total outage reaches you before a customer does. Both end in a page; neither is a dashboard someone has to notice.

### Rotation

Primary carries the pager for the week. Secondary takes over when primary has not acknowledged in five minutes, and reviews the handover at every shift change. The rota is published, the swap is agreed in the channel, and secondary is a real name, not a line nobody checks.

### Escalation

The incident commander declares severity, assigns roles and keeps the timeline. The duty manager is paged for a SEV1, for a customer-facing call, or when the IC needs authority the rota does not carry. Escalation is not punishment; it is a second pair of hands with a wider view.

Around the tiers sit the tools: one pager that owns delivery and acknowledgement, a status page customers can read, an incident channel that holds the record, and a runbook linked from every alert.

> **The honest caveat:** a rota with no handover is two people guessing in parallel. Write the state down at every change.

> **The lesson:** the system that wakes people is designed, not inherited.

## In one line

> **Page a person, not a channel.** A rotation is a promise that someone is awake.

**Test it monthly:** trigger a test page, ack it, close it
