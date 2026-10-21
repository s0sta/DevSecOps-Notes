---
id: p737
title: "The exposure pipeline"
slug: the-exposure-pipeline
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [AttackSurface, CyberSecurity, DevSecOps, CloudSecurity, VulnerabilityManagement]
source: "LinkedIn post P737 · ASM series"
linkedin_date: 2031-06-12
design: architecture
---

# The exposure pipeline

The scan found 312 exposures. The review found 40 that mattered, because 272 had no owner and no ticket.

## Quick reference

- **Probe:** HTTP probe (HTTP) · Port scan (PORT)
- **Classify:** Admin panel (ADMIN) · Storage (BUCK) · API (ROUTE)
- **Own:** Team (OWNER) · Ticket (TICK)

**Request flow:** HTTP probe → Admin panel → Team; HTTP probe → API → Team; API → Ticket; Port scan → Admin panel; Port scan → Storage → Ticket

**Around it:** Owner field (OWN) · SLA (SLA) · Evidence (EV)

## Explained

### Probe

The first tier is the export: an HTTP probe for panels and a port scan for services. It answers one question, what is reachable from outside. It does not decide severity, and it does not open a ticket.

### Classify

The second tier assigns a type: admin panel, storage, API. Each type carries a rule and a score. An admin panel at 200 outranks a login page at 200; a public bucket with a listing grant outranks a private bucket with no encryption. Classification is where the export becomes a finding.

### Own

The third tier assigns a team and a ticket. A finding without an owner is not a finding, it is a screenshot. The owner gets the evidence, the type and the deadline.

The fix is the ticket: close the panel, remove the grant, rotate the key. The pipeline's job ends when the ticket exists; the team's job ends when the rescan is clean.

### Prevention

Run the pipeline weekly, compare the new list with the previous one, and report by owner. A number that never reaches a team is a dashboard, not a programme.

> **The honest caveat:** the pipeline sees only what the probes saw. A missing probe is not a clean result; coverage is a separate metric.

> **The lesson:** an exposure without an owner is a permanent exposure.

## In one line

> **Probe, classify, then assign.** Probe sees surface, classify names it, own makes it someone's job.

**Start with probe**

```bash
curl -sI https://app.example.com
```
