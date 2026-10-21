---
id: p468
title: "Developer experience at a glance"
slug: developer-experience-at-a-glance
sections: [devsecops]
topic: "Platform engineering"
tags: [DevEx, DORA, PlatformEngineering, DevOps, SRE]
source: "LinkedIn post P468 · DevOps series"
linkedin_date: 2029-09-23
design: dashboard
---

# Developer experience at a glance

The monthly developer review had a green dashboard and one awkward question: why did the new hire take three weeks to merge anything?

## Quick reference

**Status:** This month

| Metric | Value | Note |
|:--|:--|:--|
| Lead time | **2.4 days** | median, commit to production |
| Review time | **14 h** | median, to first review |
| CI duration | **9m 40s** | median pipeline, all jobs |
| Flaky rate | **7%%** | failed, then green on retry |
| Onboarding days | **11 days** | access to first merged PR |
| Docs freshness | **82%%** | pages edited in 90 days |

## Explained

### Speed

Lead time is the median from commit to production, the DORA measure, not from the idea to the merge. Review time is the median wait for a first review, which is the number a pull request actually feels. CI duration is the median pipeline, because a mean is dragged by the slowest job.

### Health

Flaky rate is the share of failed runs that pass on a retry with no code change. It matters because a flaky suite teaches people to press rerun, and a rerun hides the real failure that follows. A suite that fails at random is not a fast suite; it is a coin toss with a log. The fix is a quarantine and an owner, not a rerun button.

### The path

Onboarding days run from access granted to the first merged pull request, which tests the golden path end to end. Docs freshness is the share of pages edited in the last ninety days; a stale runbook is worse than a missing one because it looks authoritative.

> **The honest caveat:** every tile is a proxy. Medians hide the tail, and a survey explains what the numbers cannot. SPACE adds satisfaction and flow to the numbers; DORA keeps four delivery keys.

> **The lesson:** six numbers should start one conversation, not end it.

## In one line

> **Six numbers, one conversation.** A DevEx board starts the retro; it does not replace it.

**Read the median**

```bash
gh pr list --state merged
```
