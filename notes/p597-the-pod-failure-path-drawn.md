---
id: p597
title: "The pod failure path, drawn"
slug: the-pod-failure-path-drawn
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, SRE, DevOps, CloudNative, Troubleshooting]
source: "LinkedIn post P597 · PythonFixes series"
linkedin_date: 2030-07-21
design: architecture
---

# The pod failure path, drawn

A pod can fail in three places, and the first failing step tells you which one.

## Quick reference

- **Schedule:** Scheduler (SCHED) · Node capacity (CPU) · Taints and affinity (RULE)
- **Start:** Image pull (IMG) · Config and secret (ENV)
- **Run:** Readiness probe (PROBE) · Limits and eviction (OOM)

**Request flow:** Scheduler → Node capacity → Taints and affinity; Node capacity → Image pull → Config and secret → Readiness probe → Limits and eviction

**Around it:** kubectl describe (DESC) · Events (EVT) · Exit code (EXIT)

## Explained

### Schedule

The first band holds the scheduler, node capacity and the taint rules. A pod that never gets a node stops here: no node fits the request, the selector or the taint. The scheduler writes the FailedScheduling event with the reason.

### Start

The second band is the image and the configuration. The pod has a node, but the kubelet cannot pull the image or mount the ConfigMap or Secret. The container never starts, so there is no log again.

### Run

The third band is the probe and the limits. The process starts and then exits, fails its readiness check, or is evicted when the node runs out. This is the only tier that writes application logs. Eviction is a node decision, not a container exit.

### Read it in order

The poster draws the three bands top to bottom, with arrows from the scheduler to capacity, then to the taints, the image, the config, the probe and the limits. Three chips at the bottom name the tools: kubectl describe, Events and the exit code.

> **The honest caveat:** a pod can fail twice, evicted on one node and then CrashLooping on the next. Fix the first tier that failed; the second may be a symptom.

> **The lesson:** find the tier before the fix.

## In one line

> **Find the tier before the fix.** A CrashLoop is a run failure; a Pending pod never reached run.

**Read the event**

```bash
kubectl describe pod -n prod api-7d9f
```
