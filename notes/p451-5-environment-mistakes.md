---
id: p451
title: "5 environment mistakes"
slug: 5-environment-mistakes
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, SRE, PlatformEngineering, CICD, CloudNative]
source: "LinkedIn post P451 · DevOps series"
linkedin_date: 2029-08-14
design: dontdo
---

# 5 environment mistakes

Every environment problem I have seen started as a shortcut that saved an afternoon. Five of them are common enough to name.

## Quick reference

**1.** ❌ **Prod secrets in staging** — Staging is weaker, shared and logged, so a leak there reaches production.  
✅ **One secret per environment** — Scoped values, separate rotation, separate blast radius.

**2.** ❌ **Hand-edited config on a host** — Nobody records it, and the next deploy erases it or keeps a lie.  
✅ **Change the manifest, then apply** — Reviewed, repeatable and visible in the diff.

**3.** ❌ **A snowflake server** — One machine nobody can rebuild is one disk away from an outage.  
✅ **Rebuild from code in minutes** — Replacement is routine, so failure is boring.

**4.** ❌ **Previews that never expire** — They keep running, keep costing money and keep a door open.  
✅ **Destroy on merge or close** — A sweeper deletes anything older than seven days.

**5.** ❌ **No seed data** — An empty preview proves nothing about a real query.  
✅ **Seeded, synthetic fixtures** — Every preview starts with the same known dataset.

## Explained

### The five

1. **Production secrets in staging.** Staging is weaker, shared and logged, so a leak there becomes a production incident with a staging entry point. Give each environment its own credentials and its own rotation.

2. **Hand-edited config on a host.** The change works, nobody records it, and the next deploy either erases it or preserves a state the repo does not describe. Change the manifest, then apply it.

3. **A snowflake server.** One machine that nobody can rebuild is one disk failure from an outage, and the rebuild recipe lives in someone's memory. Replace it from code in minutes.

4. **Previews that never expire.** They keep running, keep costing money and keep a URL and secrets reachable. Destroy on merge or close, and sweep anything older than seven days.

5. **No seed data.** An empty preview proves nothing about a real query, so the first realistic request fails in front of a reviewer. Seed a small synthetic dataset on every create.

### The pattern

> **The honest caveat:** each shortcut is a reasonable decision on the day it is made. The cost arrives later, in the incident review, not in the pull request.

> **The lesson:** environments are cleaned up as carefully as they are built, or they quietly become production.

## In one line

> **Clean up as carefully as you build.** A short-lived environment must actually be short-lived.

**Set a ttl**

```bash
kubectl delete ns pr142
```
