---
id: p143
title: "Fix: Kubernetes ImagePullBackOff"
slug: fix-kubernetes-imagepullbackoff
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, DevOps, Containers, Troubleshooting, CloudNative]
source: "LinkedIn post P143 · IT series"
linkedin_date: 2027-08-26
design: steps
---

# Fix: Kubernetes ImagePullBackOff

ImagePullBackOff means Kubernetes tried to pull your container image, failed, and is backing off before trying again. The pod status tells you something is wrong; the event tells you what.

## Quick reference

### Diagnose — Why can't it pull the image?

- `kubectl describe pod <name>` — The Events at the bottom give the real reason.
- **Check the tag** — manifest unknown means the name or tag is wrong.
- **Check auth** — 401 or 403 means the pull secret is missing or wrong.

### Fix — Match the name and the access

- **Correct image + tag** — Fix a typo or a tag that was never pushed.
- `kubectl create secret docker-registry regcred ...` — Credentials for a private registry.
- **imagePullSecrets: in the spec** — Point the pod at that secret, then re-apply.

### Prevent — Stop it recurring

- **Pin real tags** — Avoid latest. Use an immutable tag or a digest.
- **Verify in CI** — Confirm the image was pushed before you deploy.
- `imagePullPolicy: IfNotPresent` — Do not re-pull an image the node already has.

## Explained

### Diagnose

`kubectl describe pod <name>` and read the Events at the bottom. This is where the real error lives, and it is almost always one of three things.  
A wrong name or tag. "manifest unknown" or "not found" means the image name, tag or registry path is wrong, or that tag was never pushed. Typos and tags that only exist on a developer's laptop are the usual cause.  
An access problem. "401 Unauthorized" or "403" means the registry is private and the cluster has no valid credentials, or the pull secret is wrong.

### Fix

Correct the image and tag first if it is a typo or a missing push. Compare exactly with what is in the registry.  
For a private registry, create the credentials: kubectl create secret docker-registry regcred with the registry, username and token.  
Reference that secret with imagePullSecrets in the pod or service account, then re-apply. Kubernetes retries on its own once the problem is gone.

### Prevent

Pin real, immutable tags or digests instead of latest, so a deploy cannot point at a tag that moved or vanished.  
Verify in CI that the image was actually built and pushed before the deploy step runs.  
Set `imagePullPolicy: IfNotPresent` for stable tags so nodes do not re-pull an image they already have, which also survives a registry outage.

The habit: when a pod will not start, describe it before anything else. The status is the symptom; the event is the diagnosis.

## In one line

> **Read the event, not the status.** ImagePullBackOff is the symptom. describe has the cause.

**The first command**

```bash
kubectl describe pod <name>
```
