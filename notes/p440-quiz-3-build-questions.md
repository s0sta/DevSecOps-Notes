---
id: p440
title: "Quiz: 3 build questions"
slug: quiz-3-build-questions
sections: [devsecops]
topic: "Release & build engineering"
tags: [BuildSystems, CICD, Testing, DevOps, Engineering]
source: "LinkedIn post P440 · DevOps series"
linkedin_date: 2029-07-19
design: quiz
---

# Quiz: 3 build questions

Three questions separate a build that is fast by accident from one that is fast on purpose.

## Quick reference

**Q1. Why must a cache key hash every input?**

- a) So the key stays short
- b) So changed inputs miss the cache
- c) So the cache survives a reboot

> **Answer:** b) So changed inputs miss the cache. A key that ignores an input can return an output built from different sources. Hash what changes the result, and a change forces a miss.

**Q2. Why do hermetic builds catch missing dependencies?**

- a) They cannot reach the network
- b) They compile faster
- c) They skip the lockfile

> **Answer:** a) They cannot reach the network. A hermetic build cannot fetch what the manifest omits, so the missing dependency fails in CI instead of in production.

**Q3. Why do parallel test shards need isolation?**

- a) So each shard runs faster
- b) So shards cannot share state
- c) So the report is smaller

> **Answer:** b) So shards cannot share state. Shards that share a database, port or temp folder fail each other at random, and the flake gets blamed on the tests.

## Explained

### The cache key

1. Why must a cache key hash every input?

Because an output is only reusable for the inputs that produced it. If the key ignores the lockfile, a dependency bump returns yesterday's build with a perfect hit rate. Hash the source, the lockfile, the compiler, the flags and the environment that changes the output. A key that changes too often is expensive; a key that changes too rarely is wrong.

### Hermetic builds

2. **Why do hermetic builds catch missing dependencies?**

Because they cannot reach the network. If a build fetches a package at compile time, it passes on the machine that already has it and fails on a clean runner. Cut the network and the missing declaration fails in CI, where you can see it, instead of in a customer's environment.

### Shards

3. **Why do parallel test shards need isolation?**

Because shared state turns scheduling into luck. Two shards writing the same database row, binding the same port or reusing the same temp folder fail each other at random, and the flake gets blamed on the test. Give each shard its own database, port range and workspace.

> **The honest caveat:** a hermetic build is a direction, not a binary. Vendored dependencies and a local proxy still hide the moment a package enters, so keep the manifest the only door.

> **The lesson:** speed comes from trusting a boundary, and the boundary is what you design.

## In one line

> **Know the why, not the flag.** A build system rewards the person who can explain the miss.

**Hash the inputs**

```bash
sha256sum package-lock.json
```
