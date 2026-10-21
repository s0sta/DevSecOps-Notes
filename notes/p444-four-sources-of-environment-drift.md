---
id: p444
title: "Four sources of environment drift"
slug: four-sources-of-environment-drift
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, SRE, Configuration, CloudNative, CICD]
source: "LinkedIn post P444 · DevOps series"
linkedin_date: 2029-07-29
design: explainer
---

# Four sources of environment drift

Nothing changed, said the deploy log. The environment disagreed: the pod that worked on Tuesday failed on Thursday, and no commit explained it. Drift rarely announces itself.

## Quick reference

### Manual changes

- A hotfix typed into a console at 2 a.m.
- It works, so nobody writes it down
- The next rebuild silently removes it

### Config drift

- A value edited in a dashboard, not in Git
- Two services read the same key differently
- The repo says one thing, the runtime another

### Secret rotation

- A key rotated in one environment only
- The old credential still works somewhere
- The new key never reached the batch job

### Dependency versions

- A base image tag moved under you
- Two lockfiles resolved different versions
- Staging and prod run different majors

> **Note:** Drift is not one mistake. It is a gap you stopped measuring.

## Explained

### Manual changes

Someone edits a value in a console at 2 a.m., the fix works, and nobody writes it down. If the next apply rebuilds the resource, the change disappears and the bug returns. If nothing applies the manifest, the change stays and the definition is now a lie. Both endings are drift.

### Config drift

A value is edited in a dashboard rather than in Git. Two services read the same key and get different answers, because one reads a ConfigMap and the other reads a host env file. The repository says one thing and the runtime says another, and neither is wrong enough to fail a health check.

### Secret rotation

A key is rotated in production but not in staging, or the old credential is never revoked. A batch job keeps a static copy and keeps working until the day it does not. Rotation without revocation is a second secret, not a replacement.

### Dependency versions

A base image tag moves, a lockfile resolves differently on a rebuild, or staging installs the latest minor while production pins the previous one. The code is identical; the tree underneath it is not.

> **The honest caveat:** some drift is a deliberate hotfix. The point is not to forbid the change, it is to record it before the next person inherits it.

> **The lesson:** drift is not one mistake, it is a gap you stopped measuring.

## In one line

> **Not written down is still drift.** A change nobody recorded is a change nobody can repeat.

**Diff the baseline**

```bash
terraform plan -detailed-exitcode
```
