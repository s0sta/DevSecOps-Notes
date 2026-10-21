---
id: p464
title: "Where developer time goes"
slug: where-developer-time-goes
sections: [devsecops]
topic: "Platform engineering"
tags: [DevOps, DeveloperExperience, CICD, Productivity, Engineering]
source: "LinkedIn post P464 · DevOps series"
linkedin_date: 2029-09-13
design: explainer
---

# Where developer time goes

A developer's day is not spent typing. It is spent waiting, switching and setting up, and none of those costs appear on a sprint board.

## Quick reference

### Waiting for CI

- A ten-minute run four times a day is forty minutes
- Queue time in front of a runner is not build time
- Track the median and p90 duration per job
- Cache dependencies and split the slowest job

### Review latency

- The wait for a first reviewer, not the approval
- A large diff gets postponed, then skimmed
- Keep a review rota and a first-response target
- Measure time to first review, not time to merge

### Environment setup

- A new laptop to a running stack can take days
- Every manual step drifts from the documented one
- One command should build, seed and run the stack
- Containers make setup repeatable, not instant

### Context switching

- Every interruption costs a rebuilt mental model
- An interrupted review restarts from the first line
- Protect two-hour blocks and batch the pings
- Fewer open pull requests means fewer switches

> **Note:** Developer time is mostly queue time: measure the wait.

## Explained

### Waiting for CI

Waiting for CI is the most visible queue. A ten-minute pipeline run four times a day is forty minutes at the desk, and queue time in front of a runner is not build time. Track the median and the ninetieth percentile per job, cache dependencies, and split the slow job that blocks everything else.

### Review latency

Review latency is the wait for a first reviewer, not the time to approve. A large diff is postponed until Friday and then skimmed, which is how a two-day wait becomes a shallow review. Keep a review rota, set a first-response target people can meet, and track time to first review.

### Environment setup

Environment setup is the cost nobody budgets. A new laptop to a running service can take days of undocumented steps, and every manual step drifts. One command should build, seed and run the stack; containers make that repeatable, not instant.

### Context switching

Context switching is the tax on all three. Every interruption costs a rebuild of the mental model, and an interrupted review restarts from the first line. Protect two-hour blocks, batch the pings, and keep fewer pull requests open per person.

> **The honest caveat:** the four overlap. A slow environment makes CI feel slow, and a noisy chat tool turns every review into a context switch, so fix the queue you can see first.

> **The lesson:** developer time is mostly queue time, so measure the wait.

## In one line

> **Time is lost in the handoffs.** Optimise the queue, and the work gets faster on its own.

**Measure the wait**

```bash
gh pr list --json number,createdAt,reviews
```
