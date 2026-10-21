---
id: p389
title: "Dependency risk at a glance"
slug: dependency-risk-at-a-glance
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [DevSecOps, SupplyChain, Metrics, AppSec, CyberSecurity]
source: "LinkedIn post P389 · DevSecOps series"
linkedin_date: 2029-03-22
design: dashboard
---

# Dependency risk at a glance

A dependency review is six numbers and a decision. The dashboard is not there to look healthy; it is there to show which number changed since the last sprint.

## Quick reference

**Status:** Sprint 14 review

| Metric | Value | Note |
|:--|:--|:--|
| Outdated direct | **23%** | of 61 direct deps |
| Critical CVEs | **4** | 2 reachable from prod |
| Unmaintained | **7** | no release in 24 months |
| Licence issues | **3** | GPL in a closed product |
| Images pinned | **82%%** | of 45 by digest |
| Mean age | **14 mo** | median is 9 months |

## Explained

### The tiles

Outdated direct dependencies: 23 of 61 direct packages are behind their latest release. Direct means you chose them, so each one has an owner and a changelog. Critical CVEs: four, two of them reachable from production code. The other two are deferred with a reason. Unmaintained packages: seven with no release in 24 months. Some are finished, not abandoned, which is why this is a conversation and not a gate.

Licence issues: three, all GPL-family packages inside a closed product. The fix may be legal, architectural or a replacement, but it is not a patch. Digest-pinned images: 82 percent of 45 images are pinned by digest rather than a mutable tag. A tag can be moved; a digest cannot. That is the difference between a pointer and a promise. Mean age: 14 months, with a median of nine. The mean is pulled up by a few old dependencies that dominate the tail.

### What it means

> **The honest caveat:** every one of these numbers is a snapshot with a definition behind it. Change the definition and the dashboard changes, so write the definition next to the number.

> **The lesson:** six numbers are useful only when each one has an owner and a threshold.

## In one line

> **Count the risk, own the list.** A dashboard is a decision list, not a wall of badges.

**Export the list**

```bash
npm outdated --json > outdated.json
```
