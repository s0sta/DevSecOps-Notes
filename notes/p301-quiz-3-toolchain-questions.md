---
id: p301
title: "Quiz: 3 toolchain questions"
slug: quiz-3-toolchain-questions
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, Kubernetes, Git, CICD, SRE]
source: "LinkedIn post P301 · Visual series"
linkedin_date: 2028-08-29
design: quiz
---

# Quiz: 3 toolchain questions

Three questions come up in every toolchain review, and the answers are shorter than the arguments. Each one is really about ownership.

## Quick reference

**Q1. Your branch is shared and already pushed. Merge or rebase onto main?**

- a) Rebase, then force-push
- b) Merge main into the branch
- c) Delete the branch and start again

> **Answer:** b) Merge main into the branch. Rebase rewrites hashes other people already pulled. Merge adds a commit; nobody has to recover, and the conflict is resolved once.

**Q2. Why pin an image by digest instead of a tag?**

- a) Digests pull faster
- b) A digest cannot be repointed
- c) Tags expire after thirty days

> **Answer:** b) A digest cannot be repointed. A tag can move to a new image. The digest is the exact bytes you scanned, signed and ran, so a rollback returns to those bytes.

**Q3. What does a readiness probe actually protect?**

- a) The node from too many pods
- b) Traffic from a pod that cannot serve
- c) The container from high CPU

> **Answer:** b) Traffic from a pod that cannot serve. A failing readiness probe removes the pod from Service endpoints until it passes. Liveness is the one that restarts the container.

## Explained

### Shared branches

A shared branch, already pushed: merge or rebase? Merge. The branch is public, so its commits belong to other people too, and a rebase rewrites hashes they already pulled. Merge main into the branch, resolve once, push. Rebase your own unpushed work as much as you like, because nobody else has those hashes.

### Image digests

Why pin an image by digest? Because a tag is a pointer that can move. The digest is the exact bytes: the ones you scanned, signed and ran. Repoint the tag tomorrow and every signature stays valid for a different image, which is why a tag is not an identity.

### Readiness probes

What does a readiness probe protect? Traffic, not the container. A failing readiness probe removes the pod from Service endpoints, so no request arrives until it can serve. A liveness probe restarts the container; confusing the two turns a slow start into a restart loop that never finishes.

> **The honest caveat:** digest pinning needs an update process. Pinned images go stale, so pair the pin with a bot that opens a pull request when the tag moves.

> **The lesson:** each answer is about who owns the consequence. The shared branch, the signed bytes, the traffic.

## In one line

> **Know the why, not just the flag.** Three answers that explain most toolchain arguments.

**Read the field**

```bash
kubectl explain pod.spec.readinessProbe
```
