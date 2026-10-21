---
id: p449
title: "Environment health at a glance"
slug: environment-health-at-a-glance
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, SRE, PlatformEngineering, Observability, CloudNative]
source: "LinkedIn post P449 · DevOps series"
linkedin_date: 2029-08-09
design: dashboard
---

# Environment health at a glance

Monday stand-up starts with the same worry: something is about to break. Six tiles cover the part of it that numbers can, and the rest is a conversation.

## Quick reference

**Status:** This week

| Metric | Value | Note |
|:--|:--|:--|
| Config drift | **3 envs** | declared vs live, 24h |
| Failed deploys | **2** | of 41, last 7 days |
| Stale previews | **33%%** | 6 of 18 open |
| Missing env vars | **4** | found at boot, prod |
| Secret age | **47 days** | median, oldest 210 |
| Environment cost | **$3.8k** | staging and previews |

## Explained

### The tiles

Config drift: three environments no longer match their manifests, measured against the last applied baseline. A tile without a baseline measures nothing.

Failed deploys: two of forty-one in the last week. A failed deploy that rolled back cleanly is a different event from one that left the environment half-applied, so read the count with the rollback log.

Stale previews: six of eighteen, a third, older than seven days. Each one still costs money and still holds a URL and a set of secrets.

Missing env vars: four found at boot in production this week. The app failed fast, which is the good version; the bad version starts with a default and fails later.

Secret age: forty-seven days at the median, with the oldest at two hundred and ten. Age is not compromise, but an old credential has had more chances to leak.

Environment cost: three thousand eight hundred dollars for the month across staging and previews. A preview that no one has opened in a week is the easiest line to cut.

### The review

> **The honest caveat:** every tile is a trailing indicator, and a green board can be a week out of date. Check the timestamp before you quote it in the review.

> **The lesson:** the dashboard starts the review; it does not replace it.

## In one line

> **A green tile is not a green env.** Every tile names a question; none of them answers it.

**Count the drift**

```bash
terraform plan -detailed-exitcode
```
