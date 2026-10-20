---
id: p205
title: "Fix: Kubernetes CrashLoopBackOff"
slug: fix-kubernetes-crashloopbackoff
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CKA, DevOps, Troubleshooting, CloudNative]
source: "LinkedIn post P205 · Cloud / DevSecOps series"
linkedin_date: 2028-01-18
design: steps
---

# Fix: Kubernetes CrashLoopBackOff

CrashLoopBackOff means the container starts, crashes, and Kubernetes keeps restarting it with an increasing delay. The status tells you it is failing; the logs and events tell you why. This is the most common pod problem, and a CKA staple.

## Quick reference

### Diagnose — Why did it crash?

- `kubectl logs <pod> --previous` — Logs of the crashed container, not the new one.
- `kubectl describe pod <pod>` — Events: OOMKilled, failed probe, mount error.
- **Check the exit code** — 137 = OOM/killed, 1 = app error, 0 = exited cleanly.

### Fix — Match the cause

- **App error in logs** — Fix the config, missing env, or bad connection string.
- **OOMKilled (137)** — Raise the memory limit, or fix the leak.
- **Failing liveness probe** — The probe is too strict or the port is wrong.

### Prevent — Fewer crash loops

- **Realistic probes** — Give slow apps an initialDelaySeconds.
- **Right-size memory** — Set requests and limits from real usage.
- **Fail fast with a clear log** — Make the app say why it quit.

## Explained

### Diagnose

`kubectl logs <pod> --previous` is the key command. In a crash loop the current container has just started and has nothing useful; `--previous` shows the output of the one that actually crashed. The real error is almost always here: a missing environment variable, a refused database connection, a bad config file.  
`kubectl describe pod <pod>` shows the Events at the bottom, which catch the causes that are not in the app log: OOMKilled, a failing liveness probe, or a volume that would not mount.  
The exit code is a strong hint. 137 means killed, usually out of memory; a code of 1 or 2 is an application error; 0 means it exited cleanly, which is wrong for a long-running service.

### Fix

An app error in the logs: fix the config, the missing secret, or the connection string it cannot reach.  
OOMKilled: raise the memory limit, or fix the leak that makes it grow.  
A failing liveness probe: the probe may be too strict, or pointing at the wrong port or path, killing a healthy-but-slow app.

### Prevent

Realistic probes with an initialDelaySeconds for apps that take time to start.  
Right-sized memory requests and limits, based on real usage.  
An app that fails fast and logs clearly why, so the next crash loop takes 30 seconds to diagnose.

## In one line

> **Read --previous, not the restart count.** The crashed container's log holds the answer.

**The first command**

```bash
kubectl logs <pod> --previous
```
