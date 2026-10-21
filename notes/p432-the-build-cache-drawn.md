---
id: p432
title: "The build cache, drawn"
slug: the-build-cache-drawn
sections: [devsecops]
topic: "Release & build engineering"
tags: [DevOps, BuildSystems, CICD, Performance, Engineering]
source: "LinkedIn post P432 · DevOps series"
linkedin_date: 2029-07-01
design: architecture
---

# The build cache, drawn

Every pipeline has a cache. The only question is whether it is a cache or a rumour.

## Quick reference

- **Source:** Repository (GIT) · Lockfile (LOCK)
- **Cache:** Local cache (LOCAL) · Remote cache (S3)
- **Output:** Artifact (TAR) · Registry (OCIR)

**Request flow:** Repository → Local cache → Artifact; Lockfile → Remote cache → Registry

**Around it:** Build log (LOG)

## Explained

### Source

The top tier is the input. The repository holds the commit and the tree you meant to build. The lockfile holds the exact versions of everything that commit pulls in. Those two are the first honest inputs to a cache key: the code, and the dependencies it resolved to.

### Cache

The middle tier is where the time comes back. The local cache lives on the runner, survives between steps and dies with the machine. The remote cache lives in object storage, S3 for example, and every runner holding the same key can read it.

### Output

The bottom tier is what you keep. The artifact is the tarball or binary the pipeline hands to the next stage. The registry keeps the image layers under a digest, so a deploy can name exactly the bits it shipped.

The four arrows follow the work: repository to local cache, lockfile to remote cache, local cache to artifact, remote cache to registry. The build log sits below the tiers and watches all three. It is the only part that shows you when a hit became a miss.

> **The honest caveat:** a remote cache is shared state. A stale or poisoned entry can hand you a wrong artifact with a perfect hit rate, so scope the keys, expire the entries and sign what you store.

> **The lesson:** a cache keyed on the wrong inputs only makes the wrong build faster.

## In one line

> **Cache the work, not the failure.** A cache miss should be the exception.

**Measure it**

```bash
time make build
```
