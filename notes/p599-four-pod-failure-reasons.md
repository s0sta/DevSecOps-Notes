---
id: p599
title: "Four pod failure reasons"
slug: four-pod-failure-reasons
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, SRE, DevOps, Containers, Troubleshooting]
source: "LinkedIn post P599 · PythonFixes series"
linkedin_date: 2030-07-25
design: explainer
---

# Four pod failure reasons

Four reasons cover most failing pods, and each one sends you to a different place. Learn the phase first; the rest is a shorter list.

## Quick reference

### Pending

- The scheduler finds no node that fits
- cpu, memory, taints or an unbound claim
- No container started, so there are no logs
- Read the FailedScheduling event

### ImagePull

- The registry refused or never answered
- Missing tag, missing secret, blocked egress
- ImagePullBackOff is a retry, not a fix
- Check the pull secret and the tag

### CrashLoop

- The container starts, then exits
- Restart count climbs, the delay doubles
- Logs `--previous` hold the last words
- A probe can kill a healthy process

### Evicted

- The node ran out of memory, disk or pid
- The kubelet kills the pod, not the app
- The reason names the resource
- The controller replaces it elsewhere

## Explained

### Pending

Pending means the scheduler found no node. The request is too large, a taint is not tolerated, the claim is unbound or the affinity excludes every node. A request larger than every node's allocatable is the common case, and the event names the resource. No container started, so there are no logs.

### ImagePull

ImagePull means the node could not get the image. The tag is missing, the pull secret is absent, or the registry is unreachable. A private registry with no imagePullSecret returns the same ErrImagePull symptom as a typo in the tag. ImagePullBackOff is a retry with backoff, not a fix.

### CrashLoop

CrashLoop means the process started and exited. The restart delay doubles from 10 seconds to 5 minutes. Read `kubectl logs --previous`; the container may be healthy and the probe wrong, which is why the previous log matters.

### Evicted

Evicted means the kubelet killed the pod to protect the node. The reason names memory, ephemeral-storage or pid. The app may be the victim, not the cause, so check the node condition before you change the app. A controller recreates it, usually on another node.

> **The honest caveat:** the phase is a symptom, not a diagnosis. A pod can be Evicted and then CrashLoop on another node, and the fix belongs to the tier, not the symptom.

> **The lesson:** the phase is the first clue.

## In one line

> **The phase is the first clue.** Four reasons, four different places to look.

**Read the phase**

```bash
kubectl get pod -n prod api -o wide
```
