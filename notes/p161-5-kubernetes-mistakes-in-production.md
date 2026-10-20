---
id: p161
title: "5 Kubernetes mistakes in production"
slug: 5-kubernetes-mistakes-in-production
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CloudNative, DevOps, SRE, BestPractices]
source: "LinkedIn post P161 · IT series"
linkedin_date: 2027-10-07
design: dontdo
---

# 5 Kubernetes mistakes in production

Kubernetes is forgiving in a demo and unforgiving at scale. Five mistakes that run fine until real traffic, a node failure or a rollback exposes them.

## Quick reference

**1.** ❌ **no resource requests or limits** — One pod can starve a whole node of CPU or memory.  
✅ **set requests and limits** — The scheduler places pods well; noisy neighbours are capped.

**2.** ❌ **no readiness probe** — Traffic hits pods before they can serve it.  
✅ **readiness + liveness probes** — Traffic waits for ready; hung pods get restarted.

**3.** ❌ **one replica for a service** — A node dies and the service goes with it.  
✅ **2+ replicas, spread out** — Survive a node failure and rolling updates.

**4. Don't**

```bash
image: myapp:latest
```

Rollouts and rollbacks become unpredictable.

**Do instead**

pin a tag or digest

You always know exactly what is running.

**5.** ❌ **secrets in plain env vars in git** — Anyone with the repo has your credentials.  
✅ **Secrets + a secrets manager** — Kept out of the manifest and out of git.

## Explained

1. No resource requests or limits
   Without requests, the scheduler cannot place pods sensibly. Without limits, one pod can consume all the CPU or memory on a node and take its neighbours down. Instead: set requests so the scheduler packs pods well, and limits so no single pod can starve the rest.

2. No readiness probe
   Kubernetes assumes a pod can serve traffic the moment it starts. Without a readiness probe, requests hit pods that are still booting or connecting to the database, and users see errors during every deploy. Instead: add a readiness probe so traffic waits, and a liveness probe so a hung pod gets restarted.

3. One replica for a service
   A single pod means a single point of failure. The node it sits on reboots or dies, and the service is gone. Instead: run two or more replicas, spread across nodes with anti-affinity, so a node failure and rolling updates are both survivable.

4. `image: latest`
   latest makes rollouts and rollbacks unpredictable, because the same tag can point at different images over time. Instead: pin a specific tag or, better, a digest, so you always know exactly what is deployed.

5. Secrets as plain env vars committed to git
   Putting credentials straight into manifests in the repository hands them to anyone with read access. Instead: use Kubernetes Secrets, ideally backed by a real secrets manager, and keep them out of git.

> **The pattern:** probes, limits and replicas are what separate a demo from production.

## In one line

> **Demos hide what scale reveals.** Probes, limits and replicas are not optional in production.

**Audit one deployment**

```bash
kubectl describe deploy <name>
```
