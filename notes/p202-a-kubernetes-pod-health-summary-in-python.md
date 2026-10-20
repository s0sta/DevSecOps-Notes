---
id: p202
title: "A Kubernetes pod health summary in Python"
slug: a-kubernetes-pod-health-summary-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, Kubernetes, DevOps, SRE, CloudNative]
source: "LinkedIn post P202 · Cloud / DevSecOps series"
linkedin_date: 2028-01-11
design: code
script: pod_health.py
---

# A Kubernetes pod health summary in Python

Kubernetes phase, CKA on the horizon. kubectl get pods is fine for 10 pods and useless for 500. This script reads kubectl's JSON and prints only the pods that need attention: not Running, not fully ready, or restarting a lot. Full file attached, standard library only.

## Quick reference

The full script is at the end of this note: **pod_health.py** (standard library only, no `pip install`).

**Run it**

```bash
kubectl get pods -A -o json | python3 pod_health.py
```

**Example output**

```text
api-7d9f  0/1  7x
worker-2  0/1  12x
2 pods need attention
```

## Explained

### What it does

You pipe kubectl get pods -o json into it. It walks every pod, checks the phase, how many containers are ready, and the total restart count, and prints a short list of just the problem pods. Everything healthy is hidden, so what remains is your to-do list. It exits 1 if anything is unhealthy, so it also works in CI and alerts.

### Why read JSON

kubectl's -o json output is a stable, structured contract. Parsing it with Python is far more reliable than scraping the text table, and it lets you build exactly the view you want.

### How to use it

`kubectl get pods -A -o json | python3 pod_health.py` across all namespaces, or point it at a saved `pods.json` file. Run it from a laptop, a bastion, or a scheduled job.

The attached version shows the namespace, phase, ready count and restarts in a clean table, and flags high restart counts even when a pod currently reads Running, because a pod that keeps crashing and recovering is still a problem.

It is not a replacement for Prometheus and alerts, but it is a dependency-free triage tool you can run the moment something feels off in a cluster.

## In one line

> **Surface the problems only.** A long pod list becomes a short to-do list.

**Pipe it in**

```bash
kubectl get pods -A -o json | python3 pod_health.py
```

## Script: pod_health.py

Download: [scripts/pod_health.py](../scripts/pod_health.py)

```python
#!/usr/bin/env python3
"""pod_health.py - a quick health summary of your Kubernetes pods.

Reads `kubectl get pods -o json` and prints only what is wrong: pods that are
not Running/Succeeded, containers that are not ready, and restart counts.
Turns a long pod list into a short problem list. Standard library only.

Usage:
    kubectl get pods -A -o json | python3 pod_health.py
    python3 pod_health.py pods.json          # from a saved file

Exit code is 1 if any pod is unhealthy, so it works in CI and alerts.

By s0sta.com
"""
import json
import sys


def load(args):
    if args and args[0] != "-":
        with open(args[0]) as fh:
            return json.load(fh)
    return json.load(sys.stdin)


def main():
    data = load(sys.argv[1:])
    items = data.get("items", [])
    unhealthy = []
    for pod in items:
        meta = pod.get("metadata", {})
        name = meta.get("name", "?")
        ns = meta.get("namespace", "default")
        status = pod.get("status", {})
        phase = status.get("phase", "Unknown")
        conts = status.get("containerStatuses", []) or []
        ready = sum(1 for c in conts if c.get("ready"))
        total = len(conts)
        restarts = sum(c.get("restartCount", 0) for c in conts)
        bad = phase not in ("Running", "Succeeded") or (total and ready < total) or restarts >= 5
        if bad:
            unhealthy.append((ns, name, phase, f"{ready}/{total}", restarts))

    print(f"{len(items)} pods checked, {len(unhealthy)} need attention\n")
    if unhealthy:
        print(f"{'NAMESPACE':<16}{'POD':<40}{'PHASE':<12}{'READY':<8}RESTARTS")
        for ns, name, phase, ready, restarts in unhealthy:
            print(f"{ns:<16}{name:<40}{phase:<12}{ready:<8}{restarts}")
    else:
        print("[OK] all pods healthy")
    sys.exit(1 if unhealthy else 0)


if __name__ == "__main__":
    main()
```
