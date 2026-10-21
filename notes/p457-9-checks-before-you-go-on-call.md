---
id: p457
title: "9 checks before you go on call"
slug: 9-checks-before-you-go-on-call
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, OnCall, IncidentResponse, DevOps, Reliability]
source: "LinkedIn post P457 · DevOps series"
linkedin_date: 2029-08-28
design: checklist
---

# 9 checks before you go on call

Going on call for the first time feels like being handed a pager and a prayer. The first hour is not the moment to discover that your login expired or that nobody mentioned the migration. Nine checks, three groups, done before the handover ends.

## Quick reference

### Access

- **Pager login works today** — send a test page, ack it
- **Runbooks reachable offline** — copy in the repo
- **Prod access is read-only** — write via the IC

### Context

- **Top three alerts, explained** — what each one means
- **Dashboards bookmarked** — RED, one per service
- **Recent changes in view** — `git log --since=yesterday`

### Process

- **Escalation path has names** — a person, not a number
- **Severity one-pager** — sev2 vs sev3 in 10s
- **Handover template ready** — open, watch, changed

## Explained

### Access

Pager login works today. Send a test page, acknowledge it, close it; a login that works only in a browser will fail at 03:00 on a phone.  
Runbooks are reachable offline. If the wiki is behind SSO, keep a copy in the repo.  
Production access is read-only. Write access goes through the incident commander, and every use is logged.

### Context

Know the top three alerts. For each, say what it means, what it does not mean, and the first command you would run.  
Dashboards are bookmarked. One per service, showing rate, errors and duration, not thirty panels.  
Recent changes are in view. `git log --since=yesterday` on the deploy repo explains most new incidents before you open a terminal.

### Process

The escalation path has names. A rota with a number and no name is half a plan.  
Severity definitions fit on one page. If you cannot tell a SEV2 from a SEV3 in ten seconds, you will guess under pressure.  
The handover template is ready: what is open, what to watch, what changed.

> **The honest caveat:** nine checks do not make you ready for the incident you have not imagined. They remove the failures that have nothing to do with it.

> **The lesson:** preparation is the part of on-call you control.

## In one line

> **Know the system before it pages.** Nine checks cost an hour; the first bad night costs more.

**The first check:** page yourself, then ack it
