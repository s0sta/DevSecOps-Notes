---
id: p461
title: "On-call terms, decoded"
slug: on-call-terms-decoded
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, OnCall, IncidentResponse, DevOps, Reliability]
source: "LinkedIn post P461 · DevOps series"
linkedin_date: 2029-09-06
design: reveal
---

# On-call terms, decoded

On-call has a vocabulary of its own, and most of it is learned at the worst possible moment. Six terms, in the order you meet them.

## Quick reference

- **page** — A machine asking a human to act now. It goes to a pager, not a channel that can be muted.
- **ack** — A human confirming they have the page. It stops the escalation timer, not the incident.
- **escalation** — Waking the next person because the first did not answer, or cannot fix it.
- **incident commander** — Runs the response: severity, roles, timeline and communication, not necessarily the fix.
- **sev level** — The agreed label for impact. It decides who is paged and how often you update.
- **postmortem** — The review after the fact: timeline, causes and actions with owners and dates.

## Explained

### The terms

A page is a request for a human to act now, sent by the pager rather than a chat message that can be muted. An ack is the acknowledgement that a human has seen it; it stops the escalation timer, not the incident.

Escalation is the next person in line being woken because the first did not answer or cannot fix it. It should be automatic and boring, not a judgement call made at 03:00.

The incident commander runs the response: severity, roles, timeline and communication. They are not necessarily the best debugger in the room, and on a SEV1 they should not be typing fixes.

A sev level is the agreed label for impact, from total outage to cosmetic. It decides who is paged and how often you update, which is why the definition belongs in writing.

A postmortem is the review after the fact: what happened, what made it worse, what changes. Blameless refers to people, not to actions.

> **The honest caveat:** every team bends these words. The only thing that matters is that everyone in the rota means the same thing by them, and that the meanings are written down.

> **The lesson:** shared words are the first tool of a shared response.

## In one line

> **Learn the words, share the pager.** A shared vocabulary is the first tool of a shared response.

**Write them down:** page, ack, escalation, IC, sev, postmortem
