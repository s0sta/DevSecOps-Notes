---
id: p299
title: "5 CI/CD mistakes and the fix for each"
slug: 5-ci-cd-mistakes-and-the-fix-for-each
sections: [devsecops]
topic: "Git & CI/CD"
tags: [CICD, DevOps, DevSecOps, GitOps, SRE]
source: "LinkedIn post P299 · Visual series"
linkedin_date: 2028-08-24
design: dontdo
---

# 5 CI/CD mistakes and the fix for each

The pipeline is green, the release is broken, and the post-mortem finds the same five shortcuts. None of them looked like a mistake on the day.

## Quick reference

**1.** ❌ **Hotfix built on a laptop** — Nothing records the compiler, the versions or the person.  
✅ **One pipeline for every change** — Run the emergency through it; a bypass is untested.

**2.** ❌ **Rebuild the image per stage** — Staging tested a different binary from the one that ships.  
✅ **Build once, promote the digest** — The same artefact moves through every environment.

**3.** ❌ **Secrets echoed in job logs** — A debug echo puts the token in a log kept for ninety days.  
✅ **Mask every secret value** — Mask values in CI and keep them in the secret store.

**4.** ❌ **Deploy job runs as cluster-admin** — The runner can delete every namespace it can see.  
✅ **Namespace-scoped deploy role** — One namespace and one verb set is enough to deploy.

**5.** ❌ **Retry flaky tests until green** — The retry hides a race that appears under production load.  
✅ **Quarantine and fix the test** — Quarantine it, fix it, or delete it; do not normalise red.

## Explained

### The five

1. **A hotfix built on a laptop.** Nothing records the compiler, the dependency versions or the person, so the binary cannot be rebuilt. Run the emergency through the pipeline; a bypass is a second process nobody tests.
   \2. The image rebuilt per stage. Staging built one image and production built another from the same commit, and only one was tested. Build once, promote the digest.
   \3. Secrets echoed in job logs. A debug step prints the environment, the token lands in a log kept for ninety days, and the leak is one search away. Mask values and use the secret store.
   \4. A deploy job with cluster-admin. The runner is the most valuable credential in the building and can delete every namespace. Scope it to one namespace and one verb set.
   \5. Flaky tests retried until green. The retry hides a race that appears under load in production. Quarantine the test, fix it or delete it, but do not teach the team that green means nothing.

### Why they survive

Each one saves a minute today and spends an hour in the incident review later.

> **The honest caveat:** a retry is right for a network timeout. The mistake is a retry with no ticket, no owner and no count.

> **The lesson:** a pipeline is a series of promises. Every shortcut breaks one, and production collects the debt.

## In one line

> **The shortcut is the incident.** Every skipped step is a future 2 a.m. page.

**Trace the run**

```bash
gh run list --limit 5
```
