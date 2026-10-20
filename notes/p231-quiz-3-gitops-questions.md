---
id: p231
title: "Quiz: 3 GitOps questions"
slug: quiz-3-gitops-questions
sections: [devsecops]
topic: "GitOps & Helm"
tags: [GitOps, ArgoCD, Kubernetes, SRE, DevOps]
source: "LinkedIn post P231 · Platform series"
linkedin_date: 2028-03-19
design: quiz
---

# Quiz: 3 GitOps questions

Three GitOps questions I ask in interviews, because the answers separate people who run auto-sync from people who understand it. No CLI trivia, just the trade-offs.

## Quick reference

**Q1. Why does a :latest tag break rollbacks?**

- a) It pulls slower
- b) The tag can point somewhere new
- c) Kubernetes refuses it

> **Answer:** b) The tag can point somewhere new. A rollback replays the manifest, not the image. If latest moved, you deploy different bits. Pin the digest.

**Q2. What does prune actually do?**

- a) Deletes resources removed from Git
- b) Deletes old ReplicaSets
- c) Clears the Argo CD cache

> **Answer:** a) Deletes resources removed from Git. Prune deletes live resources no longer in Git. Off by default. With it on, one deleted manifest deletes the resource.

**Q3. Why diff before sync in production?**

- a) It is faster
- b) It shows the change before applying it
- c) It skips the health check

> **Answer:** b) It shows the change before applying it. A sync is a deployment. The diff shows the exact change while nothing has been applied yet.

## Explained

### Three questions

1. **Why does a :latest tag break rollbacks?**

> **Answer:** the tag can point somewhere new. A rollback replays the manifest, not the image, so if latest moved, the rollback deploys different bits or nothing at all. Pin the digest and the history means something. That is why the digest is the only safe reference.

2. **What does prune actually do?**

> **Answer:** it deletes live resources that are no longer in Git. It is off by default. With it on, deleting a manifest deletes the resource, including a database that was removed by accident. Diff first, then prune. And prune runs after the diff, never instead of it.

3. **Why diff before sync in production?**

> **Answer:** a sync is a deployment. The diff shows the exact change before anything is applied. It is the cheapest review you will ever do, and the only one that sees the live cluster. It is also the point where a surprise shows up before a user does.

### The pattern

> **The lesson:** the commands are simple; the consequences are not. A quiz is cheap; an incident is not.

> **The honest caveat:** a clean diff does not prove the app works. Only health checks and real traffic do.

## In one line

> **Know the why, not the verb.** GitOps is a set of trade-offs, not a list of commands.

**Check the history**

```bash
argocd app history api
```
