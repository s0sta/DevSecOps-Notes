---
id: p434
title: "Why builds are slow"
slug: why-builds-are-slow
sections: [devsecops]
topic: "Release & build engineering"
tags: [DevOps, CICD, BuildSystems, Performance, Engineering]
source: "LinkedIn post P434 · DevOps series"
linkedin_date: 2029-07-05
design: explainer
---

# Why builds are slow

A build that takes eleven minutes is not one problem. It is usually four, and the loudest one is rarely the expensive one.

## Quick reference

### Cold cache

- Every layer rebuilt from scratch
- Dependencies downloaded again
- Usually a cache key problem

### No parallelism

- One job, one core, the rest idle
- `make -j` is not the default
- One test runner walks the suite

### Network

- Every run pulls base images
- Registries throttle large pulls
- A proxy adds a hop to each fetch

### Test suite

- The suite only ever grows
- Integration tests wait on services
- Nobody shards the slowest stage

> **Note:** Measure before you optimise: a build without numbers is a rumour.

## Explained

### Cold cache

Every layer is rebuilt because nothing survived the previous run. Dependencies download again, and the first build on a new runner pays for it. Most of the time the cache is not missing; it is keyed on something that changes every run, such as a timestamp or a branch name.

### No parallelism

One job runs the steps in order, on one core, while the rest of the machine idles. `make without -j` compiles one file at a time. A single test runner walks the suite serially. The fix is usually a flag and a larger runner, not a rewrite.

### Network

Every run pulls base images and packages from registries that may be slow, throttled or proxied. A layer that installs four hundred packages pays that cost on every cold build, and the bill arrives as wall clock.

### Test suite

The suite grows every sprint and nobody deletes a test. Integration tests wait on real services, and the whole suite gates every merge. Nobody shards it, and it is the phase teams optimise last.

The note under the panels is the rule: measure before you optimise, because a build without numbers is a rumour.

> **The honest caveat:** a faster build is not a better one. Shaving minutes by skipping tests or caching aggressively just ships the bug sooner.

> **The lesson:** fix the cause you can measure, not the one that sounds modern.

## In one line

> **Slow is a symptom, not a verdict.** The fix is a measurement away.

**Time each step**

```bash
time make -j8 build
```
