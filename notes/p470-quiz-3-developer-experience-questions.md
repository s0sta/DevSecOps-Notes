---
id: p470
title: "Quiz: 3 developer experience questions"
slug: quiz-3-developer-experience-questions
sections: [devsecops]
topic: "Platform engineering"
tags: [DevEx, DORA, CodeReview, PlatformEngineering, DevOps]
source: "LinkedIn post P470 · DevOps series"
linkedin_date: 2029-09-27
design: quiz
---

# Quiz: 3 developer experience questions

Three questions separate a team that measures its delivery from one that measures how tired it is. Answer before you read on.

## Quick reference

**Q1. Why does lead time beat utilisation as a productivity measure?**

- a) Busy people ship more
- b) It counts the waiting
- c) Utilisation is easier to chart

> **Answer:** b) It counts the waiting. Utilisation counts busy time; lead time counts elapsed time to production. In a queue, ninety per cent busy means waits about nine times the work.

**Q2. Why does pull request size predict how long the review takes?**

- a) Large diffs get postponed
- b) Large diffs contain more bugs
- c) Reviewers prefer small teams

> **Answer:** a) Large diffs get postponed. A reviewer batches a large diff, then skims it. Past roughly four hundred changed lines the wait grows and the reading gets shallower.

**Q3. Why is onboarding time a platform metric, not a hiring metric?**

- a) It measures the golden path
- b) It measures the new hire
- c) It measures the recruiter

> **Answer:** a) It measures the golden path. Time to a first merged pull request exercises access, docs, environments and CI at once. A slow result is a finding about the platform.

## Explained

### Question one

Why does lead time beat utilisation? Utilisation counts the time people spend busy; lead time counts the time a change takes to reach production. In any queue, high utilisation means long waits: at ninety per cent busy, the wait is roughly nine times the work in the simplest model. A team at full capacity has no slack to absorb a review, an incident or a bad day.

### Question two

Why does pull request size predict review delay? A reviewer batches a large diff, postpones it, then skims it. Past roughly four hundred changed lines, the wait grows and the reading gets shallower, so the review that was meant to catch defects catches fewer of them.

### Question three

Why is onboarding time a platform metric? Time to a first merged pull request exercises access, documentation, environments and CI in one path. A slow result is a finding about the platform, not about the new hire's ability, and the fix is usually a missing template or a manual grant.

> **The honest caveat:** these are rules of thumb, not laws. A small diff can wait for a missing reviewer, and a fast onboarding can hide a team that never gives the new hire real work.

> **The lesson:** the queue is the system, and the person is rarely the bottleneck.

## In one line

> **Measure the wait, not the busy.** Three questions, one theme: queues beat effort.

**Ask a new hire**

```bash
gh pr list --author @me
```
