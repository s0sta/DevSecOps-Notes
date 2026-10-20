---
id: p153
title: "A zero-downtime deployment, minute by minute"
slug: a-zero-downtime-deployment-minute-by-minute
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevOps, Kubernetes, CICD, SRE, CloudNative]
source: "LinkedIn post P153 · IT series"
linkedin_date: 2027-09-19
design: timeline
---

# A zero-downtime deployment, minute by minute

Shipping a new version without any downtime is not luck. It is a sequence of steps, each protecting users from the change happening underneath them. Here is how a rolling deployment works, minute by minute.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **T-0** | New version built | CI produces an image, tagged with the commit. |
| **T+1** | Rolling update starts | New pods start alongside the old ones. |
| **T+2** | Readiness checks | Traffic only reaches a new pod once it is ready. |
| **T+4** | Old pods drain | They finish in-flight requests, then stop. |
| **T+6** | All traffic on new | The rollout completes. Users noticed nothing. |
| **T+7** | Rollback stays ready | One command returns to the old version if needed. |

## Explained

T-0, new version built. CI finishes and produces a container image tagged with the exact commit. The thing that was tested is the thing that will ship.

T+1, rolling update starts. Instead of stopping the old version and starting the new one, the platform starts new pods alongside the old ones. For a moment both versions run together, which is why your app must tolerate that.

T+2, readiness checks. Each new pod must pass its readiness probe before it receives any traffic. A pod that is still starting up, connecting to the database or warming a cache gets no users until it says it is ready. This single mechanism prevents most "deploy broke the site" moments.

T+4, old pods drain. As new pods become ready, old ones are told to stop. A graceful shutdown lets them finish the requests already in flight and close connections cleanly, rather than dropping users mid-request.

T+6, all traffic on new. The last old pod is gone, every request now hits the new version, and users noticed nothing. No maintenance page, no dropped connections.

T+7, rollback stays ready. The previous version is one command away. If error rates climb, kubectl rollout undo returns to it in seconds.

The two things that make it work: readiness checks so traffic waits for healthy pods, and graceful shutdown so leaving pods finish their work.

## In one line

> **Deploys should be boring.** Health checks and rolling updates make downtime optional.

**Watch it roll**

```bash
kubectl rollout status deploy/api
```
