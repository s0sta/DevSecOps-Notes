---
id: p459
title: "5 postmortem mistakes"
slug: 5-postmortem-mistakes
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, Postmortem, IncidentResponse, DevOps, Reliability]
source: "LinkedIn post P459 · DevOps series"
linkedin_date: 2029-09-02
design: dontdo
---

# 5 postmortem mistakes

Most postmortems are written by tired people who want to close the ticket. That is exactly why the same five mistakes appear in review after review.

## Quick reference

**1.** ❌ **Name the engineer** — It ends the conversation early.  
✅ **Name the condition** — Fix the guardrail that allowed it.

**2.** ❌ **Action with no owner** — A wish, not a task.  
✅ **One named owner** — They accept it in the document.

**3.** ❌ **No deadline** — It slips for a quarter.  
✅ **A date in the tracker** — Even if the date later moves.

**4.** ❌ **Fix lives in a wiki** — Nobody reads it at 3 a.m.  
✅ **Change code or config** — A test that fails next time.

**5.** ❌ **Review stays in the team** — Four people learn, nobody else.  
✅ **Publish and discuss** — The organisation learns from one night.

## Explained

### The five

1. **Blame.** Naming the engineer who ran the command ends the learning, because everyone else stops talking. Name the condition that made the command look safe: the missing guardrail, the alert nobody saw.
   \2. No owner. An action with no name is a wish. Every action gets one person, not a team, and that person accepts it in the document.
   \3. No deadline. An action with no date is a wish with a longer horizon. Put a date in the tracker, even if it slips later.
   \4. No code change. If the fix lives in a wiki page, it will not hold. The strongest action changes a pipeline, a default, a check or a test.
   \5. Not shared. A review read by four people fixes four people's habits. Post it where the organisation reads, and repeat the finding somewhere public.

### What they share

Each one is a way to finish the document without changing the system. The document looks complete, the incident returns, and the next review repeats the same paragraphs.

> **The honest caveat:** a blameless review is not a consequence-free one. It removes blame from people so the facts can surface; performance problems are handled elsewhere, privately.

> **The lesson:** a postmortem is finished when the system is different, not when the document is signed.

## In one line

> **Change the system, not the name.** A review is finished when the system is different.

**Check the actions:** owner, date, and a merged change
