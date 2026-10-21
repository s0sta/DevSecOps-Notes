---
id: p441
title: "6 numbers in a build pipeline"
slug: 6-numbers-in-a-build-pipeline
sections: [devsecops]
topic: "Release & build engineering"
tags: [CICD, BuildSystems, Performance, DevOps, SRE]
source: "LinkedIn post P441 · DevOps series"
linkedin_date: 2029-07-22
design: numbers
---

# 6 numbers in a build pipeline

A build pipeline is a chain of waiting rooms, and the only one people time is the build.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **85%** | Cache hit rate | A working target; below 60% the key is usually wrong. | cache |
| **3m** | Queue time | The wait before a runner starts; invisible in the log. | queue |
| **6m** | Build time | First instruction to pushed image, at p50 and p95. | build |
| **8m** | Test time | The suite that gates the merge; shard before rewriting. | test |
| **180MB** | Artifact size | Pulled by every environment that deploys it. | image |
| **2%** | Flake rate | Two runs in a hundred fail for no reason. Trust goes. | flaky |

## Explained

### Cache and queue

85% cache hit rate is a working target: most steps replay, and the misses are the ones that changed. Below 60%, the key is usually wrong, not the cache. 3m queue time is the wait before a runner picks the job up. It is invisible in the build log and very visible to the developer who is waiting.

### Build and test

6m build time is the step from first instruction to pushed image, measured at p50 and p95. 8m test time is the suite that gates the merge. Shard it before you rewrite it, because a suite that long is mostly waiting, and a rewrite is the expensive way to find that out.

### Size and flake

180MB artifact size is pulled by every environment that deploys it, so a fat image is a tax on every node. 2% flake rate means two runs in a hundred fail for no reason, which is enough to teach the team to press re-run and stop reading failures.

> **The honest caveat:** none of these is universal. A fifteen-minute build is fine for firmware and a scandal for a web API, so compare against your own last ten runs, not someone else's slide.

> **The lesson:** the pipeline is the sum of the parts nobody timed.

## In one line

> **Measure the queue, not just the build.** The pipeline is the sum of the parts nobody timed.

**Export the jobs**

```bash
gh run view 123 --json jobs
```
