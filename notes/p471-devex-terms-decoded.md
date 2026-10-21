---
id: p471
title: "DevEx terms, decoded"
slug: devex-terms-decoded
sections: [devsecops]
topic: "Platform engineering"
tags: [DevEx, PlatformEngineering, DevOps, DORA, SoftwareEngineering]
source: "LinkedIn post P471 · DevOps series"
linkedin_date: 2029-09-30
design: reveal
---

# DevEx terms, decoded

Six terms come up in every developer productivity review, and two of them are usually being defined differently by the people in the room.

## Quick reference

- **Lead time** — Commit to production in DORA; request to delivery in lean. Name the clock before comparing.
- **Cycle time** — Start of work to done. It leaves out the queue that lead time includes.
- **WIP** — Work in progress: started, not finished. Every extra item makes every queue longer.
- **Toil** — Manual, repetitive, automatable work that grows with the service, not with its value.
- **Cognitive load** — The working memory a task demands. A platform should carry it, not the team.
- **Inner source** — Open-source habits inside one company: internal repos, issues and pull requests anyone may send.

## Explained

### Time

Lead time is the clock from a change to production. DORA starts it at the commit; lean starts it at the request, which is why the same team can report two different numbers. Cycle time starts when work starts and ends when it is done, so it leaves out the queue that lead time includes.

### Flow

WIP, work in progress, is everything started and not finished. Every extra item makes every queue longer, which is the whole argument for a WIP limit. Toil is manual, repetitive, automatable work that grows with the service rather than with the value it delivers.

### People

Cognitive load is the working memory a task demands; a platform should carry it so the team does not have to. Inner source is open-source practice inside one company: internal repositories, issues and pull requests that anyone may send.

> **The honest caveat:** every definition here is a choice. Two teams can both say lead time and mean different clocks, so put the start and the stop in the metric name.

> **The lesson:** a shared definition is worth more than a precise one nobody shares.

That is the series. Fifty posts, from a release strategy to a first merged pull request, five phases and ten Python scripts. Thank you for following along.

## In one line

> **Name the clock, then the number.** A metric without a definition is an opinion.

**Define it first**

```bash
grep -rn 'lead time' docs/
```
