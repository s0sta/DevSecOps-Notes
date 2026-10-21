---
id: p601
title: "Quiz: 3 Kubernetes failure questions"
slug: quiz-3-kubernetes-failure-questions
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, SRE, DevOps, CloudNative, Troubleshooting]
source: "LinkedIn post P601 · PythonFixes series"
linkedin_date: 2030-07-30
design: quiz
---

# Quiz: 3 Kubernetes failure questions

Three questions separate a kubectl guess from a diagnosis, and all three come back in a review.

## Quick reference

**Q1. Why does a Pending pod have no logs?**

- a) It never started a container
- b) The log driver is disabled
- c) The pod is on an unscheduled node

> **Answer:** a) It never started a container. A Pending pod has not been placed on a node, so no image was pulled and no process ran. The evidence is the FailedScheduling event, not a log.

**Q2. What does an eviction reason tell you?**

- a) Which node resource ran out
- b) Which container crashed
- c) Which probe failed

> **Answer:** a) Which node resource ran out. Evicted means the kubelet killed the pod to protect the node. The message names memory, storage or pid, which points at capacity or a leak, not at the app.

**Q3. Why does CrashLoop backoff grow?**

- a) To give the node time to recover
- b) To slow a failing restart loop
- c) To wait for the image pull

> **Answer:** b) To slow a failing restart loop. Each restart doubles the wait from 10 seconds up to 5 minutes. It protects the kubelet and the network, and a fast fix still waits for the current backoff.

## Explained

### Question one

Why does a Pending pod have no logs? Because it never started a container. The scheduler could not place it, so no image was pulled and no process ran. The FailedScheduling event is the evidence; a log search on a Pending pod returns nothing, and that nothing is expected.

### Question two

What does an eviction reason tell you? Which node resource ran out. Evicted means the kubelet killed the pod to protect the node, and the message names memory, ephemeral-storage or pid. It is a node-level event, not an application error, so the pod's exit code is not the place to look. The node, not the app, is the first suspect.

### Question three

Why does CrashLoop backoff grow? To slow a failing restart loop. Each restart doubles the wait from 10 seconds up to 5 minutes. It protects the kubelet and the network, and a fast fix still waits for the current backoff. The delay resets only after a stable run, not after a fix.

> **The honest caveat:** backoff and eviction are both protection mechanisms, one for the restart loop and one for the node. Neither fixes the underlying fault, so the fault is still yours to find.

> **The lesson:** know the phase, skip the guess.

## In one line

> **Know the phase, skip the guess.** Three answers that save a wrong kubectl command.

**Read the phase**

```bash
kubectl get pod -n prod api -o wide
```
