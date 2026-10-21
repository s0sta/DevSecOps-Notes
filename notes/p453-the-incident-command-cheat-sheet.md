---
id: p453
title: "The incident command cheat sheet"
slug: the-incident-command-cheat-sheet
sections: [devsecops]
topic: "Observability & SRE"
tags: [IncidentResponse, SRE, OnCall, DevOps, IncidentCommand]
source: "LinkedIn post P453 · DevOps series"
linkedin_date: 2029-08-19
design: cheatsheet
---

# The incident command cheat sheet

An incident starts as a strange graph and ends as a written record. In between, four blocks decide whether the next hour is calm or chaotic.

## Quick reference

### Declare

```bash
/incident declare sev2 checkout
date -u +%FT%TZ
page IC: @ana, secondary: @sam
channel: #inc-2026-04-17-checkout
SEV2 declared by @ana at 14:05Z
```

### Roles

```bash
IC: @ana  OPS: @sam  COMMS: @lee
scribe: @dev  liaison: @ops
role swap at 16:00Z, both ack
SEV3 to SEV2 by IC at 15:20Z
handover: IC @ana to @sam, 22:00Z
```

### Comms

```bash
Status: investigating, next 14:30Z
Status: identified, rollback started
Status: monitoring, errors flat 10 min
Status: resolved at 14:52Z
next update in 30 min, even if quiet
```

### Close

```bash
kubectl rollout undo deploy/api
git revert --no-edit 3f2a1c9
close after 30 min clean, not 1 min
review booked within 48 hours
timeline exported to the incident doc
```

## Explained

### Declare

Say it out loud before you understand it. Declaring a SEV2 opens a channel, gives the work a name and tells people to stop guessing in DMs. Stamp the start with `date -u +%FT%TZ`, page the incident commander and the secondary, and publish the channel name and the first update in the same minute. A slow declaration is the easiest way to lose ten minutes.

### Roles

One incident commander, one operations lead, one communications lead, one scribe. Post the names in the channel: IC: @ana OPS: @sam COMMS: @lee. The scribe writes timestamps and decisions, not opinions. When someone joins, they read the roles before they type.

### Comms

The status page gets a sentence, not a paragraph: Status: investigating, next update 14:30Z. Then identified, monitoring and resolved, each with the same shape and a time. Update every 30 minutes even when nothing has changed, because silence reads as chaos to the customer.

### Close

Undo the change with `kubectl rollout undo deploy/api` and confirm the graphs. Close on evidence: thirty minutes clean, not one. Book the review within 48 hours while memory is fresh, and put the timeline in the incident document.

> **The honest caveat:** templates feel bureaucratic at 3 a.m. They are the reason you can write a clear update while half awake.

> **The lesson:** the channel is the record, so write for the person who was not there.

## In one line

> **Say it once, say it early.** The channel is the record. Write for the person who was not there.

**Write the first update:** Status: investigating, 14:05Z
