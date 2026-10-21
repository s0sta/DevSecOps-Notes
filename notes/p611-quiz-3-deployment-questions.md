---
id: p611
title: "Quiz: 3 deployment questions"
slug: quiz-3-deployment-questions
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevOps, Kubernetes, CICD, Python, SRE]
source: "LinkedIn post P611 · PythonFixes series"
linkedin_date: 2030-08-22
design: quiz
---

# Quiz: 3 deployment questions

Three questions come back in every release review, and the answers separate a deploy from a guess.

## Quick reference

**Q1. Why is an image tag not an artifact?**

- a) It can point to a different digest
- b) Tags are encrypted strings
- c) Tags are deleted after deploy

> **Answer:** a) It can point to a different digest. A tag is a mutable label. The same tag can resolve to new bytes, so it names a version, not the artifact. Pin the digest.

**Q2. What makes a rollback target?**

- a) A previous ReplicaSet at revision N-1
- b) A database backup from last night
- c) The latest image tag

> **Answer:** a) A previous ReplicaSet at revision N-1. A Deployment keeps old ReplicaSets up to revisionHistoryLimit. The target is a previous revision present and scaled to zero; a limit of 0 deletes it.

**Q3. Why does a smoke test need an assertion?**

- a) A 200 can come from the old pods
- b) Curl already checks the status
- c) Logs are not kept long enough

> **Answer:** a) A 200 can come from the old pods. A 200 can be served by the old ReplicaSet, a cache or a login page. Assert a value only the new release returns, and fail the job when it is absent.

## Explained

### The tag

Question one: why is an image tag not an artifact? A tag is a mutable label. The same tag can resolve to new bytes on the next pull, so it names a version, not the thing that ran. A digest names the bytes. If the release record holds only a tag, nobody can prove which artifact was live at 03:00.

### The target

Question two: what makes a rollback target? A Deployment keeps old ReplicaSets up to revisionHistoryLimit, and the target is the previous revision still present and scaled to zero. If the limit is 0, or the old set was deleted, rollout undo has nothing to scale up.

### The assertion

Question three: why does a smoke test need an assertion? A request that returns 200 can be served by the old ReplicaSet, a cache or a login page. The status code proves that something answered. An assertion on a value only the new release returns proves that the new code answered, and it fails the job when the value is missing.

The three connect: a digest pins the artifact, a target makes it reversible, and an assertion proves the new one is live. Remove any one and the other two report success without evidence.

> **The honest caveat:** passing this quiz does not make a release safe; the gate and the check do.

> **The lesson:** green is a colour, not a proof.

## In one line

> **Green is not the same as right.** Three questions to ask before the next release.

**Check one pod**

```bash
kubectl get pod api-7d9f -o yaml
```
