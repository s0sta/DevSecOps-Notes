---
id: p115
title: "9 kubectl commands for troubleshooting"
slug: 9-kubectl-commands-for-troubleshooting
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, DevOps, CloudNative, Containers, SRE]
source: "LinkedIn post P115 · Linux + IT series"
linkedin_date: 2027-06-22
design: steps
---

# 9 kubectl commands for troubleshooting

Kubernetes tells you a lot about why something failed, if you know which command to ask. Nine kubectl commands for when pods misbehave.

## Quick reference

### See — What is the cluster saying?

```bash
# Every pod in every namespace, with status and restarts.
kubectl get pods -A
# The events at the bottom explain most failures.
kubectl describe pod api-7d9f8c6b5-x2kqp
# Recent cluster events, newest at the bottom.
kubectl get events --sort-by=.lastTimestamp
```

### Debug — Look inside the pod

```bash
# Logs of the crashed container, not the new one.
kubectl logs api-7d9f8c6b5-x2kqp --previous
# A shell inside a running pod.
kubectl exec -it web-5c8d7f9d4-mm7tz -- sh
# CPU and memory per pod. Needs metrics-server.
kubectl top pods -n shop
```

### Change — Roll forward or back

```bash
# Watch a deployment finish, or see it get stuck.
kubectl rollout status deploy/api
# Back to the previous version in seconds.
kubectl rollout undo deploy/api
# Reach a service from your laptop, no ingress needed.
kubectl port-forward svc/api 8080:80
```

## Explained

### See

`kubectl get pods -A` shows every pod in every namespace, with status and restart count. A high restart count is a clue even when the status says Running.  
kubectl describe pod \<name> has an Events section at the bottom that explains most problems: image pull errors, failed health checks, OOMKilled, or "0/3 nodes are available" for a Pending pod.  
`kubectl get events --sort-by=.lastTimestamp` shows recent events across the namespace in time order. Useful when you do not know which pod to look at yet.

### Debug

`kubectl logs <pod> --previous`. In a crash loop, the current container has just started and has nothing useful to say. `--previous` shows the logs of the one that crashed.  
`kubectl exec -it <pod>` -- sh opens a shell inside a running pod. Check environment variables, config files and whether it can reach its database.  
`kubectl top pods -n shop` shows CPU and memory per pod, compared with what you set in requests and limits. It needs metrics-server installed.

### Change

`kubectl rollout status deploy/api` lets you watch a deployment roll out. If new pods never become ready, it stops and tells you.  
`kubectl rollout undo deploy/api` goes back to the previous version. The fastest fix for a bad deploy, while you investigate.  
`kubectl port-forward svc/api 8080:80` reaches a service from your laptop through the API server, without exposing it publicly.

The order that saves the most time: describe, events, logs `--previous`. Then change something.

CrashLoopBackOff is a symptom, not a cause.

## In one line

> **CrashLoopBackOff is a symptom.** The reason is in describe, events and the previous logs.

**The first two**

```bash
kubectl describe pod <name>; kubectl logs <name> --previous
```
