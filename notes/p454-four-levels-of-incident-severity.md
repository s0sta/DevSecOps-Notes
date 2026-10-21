---
id: p454
title: "Four levels of incident severity"
slug: four-levels-of-incident-severity
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, IncidentResponse, OnCall, DevOps, Reliability]
source: "LinkedIn post P454 · DevOps series"
linkedin_date: 2029-08-21
design: explainer
---

# Four levels of incident severity

A SEV1 and a SEV4 both mean something is wrong. The difference is who is woken, how often you speak, and how much of the company stops to watch.

## Quick reference

### SEV1 - Total outage

- Customer-facing outage, data loss or breach
- Paged: IC, service owners, duty manager
- War room, status page, update every 15 min
- Fix first; the full review comes after

### SEV2 - Major degradation

- A core journey is broken or badly slow
- Paged: IC and the owning team
- Manager informed, not woken
- Update every 30 min; decide rollback in 1h

### SEV3 - Limited impact

- One segment, feature or small customer set
- Paged: on-call engineer, ticket to team
- Handled in hours, update once a day
- Escalate if the impact turns out wider

### SEV4 - Cosmetic or internal

- Cosmetic or internal, no customer impact
- No page: a ticket in the backlog
- Fixed in normal working hours
- Re-triage quietly if the signal changes

> **Note:** The names differ by company; the shape does not: impact decides who is woken.

## Explained

### SEV1: total outage

Customer-facing outage, data loss or a security breach. Page the incident commander, the service owners and the duty manager. Open a war room, update the status page, and post an update every 15 minutes until it is over. Fix first; the review comes after.

### SEV2: major degradation

A core journey is broken or badly slow, and a workaround may exist. Page the IC and the owning team, and inform the manager rather than paging them. Update every 30 minutes, and decide on a rollback within the first hour.

### SEV3: limited impact

One segment, one feature or a small set of customers. Page the on-call engineer, open a ticket for the team, and handle it in working hours if nobody is blocked. Update daily, and escalate the moment the impact turns out wider.

### SEV4: cosmetic or internal

No customer impact: a broken report, a noisy log, a typo in the console. No page. A ticket in the backlog, fixed in normal hours, and re-triaged if the signal changes.

The labels and the paging rules differ by company; the shape does not. Impact decides who is woken, and a written definition lets someone downgrade an incident without an argument.

> **The honest caveat:** a severity matrix nobody has read at 3 a.m. is decoration. Put the four lines in the alert template.

> **The lesson:** declare early, then let evidence move the level.

## In one line

> **Severity decides who wakes up.** Declare early, then downgrade it with evidence.

**Define sev2:** major degradation, workaround exists
