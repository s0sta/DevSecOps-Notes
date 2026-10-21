---
id: p600
title: "9 commands to triage a failing pod"
slug: 9-commands-to-triage-a-failing-pod
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, kubectl, SRE, DevOps, CommandLine]
source: "LinkedIn post P600 · PythonFixes series"
linkedin_date: 2030-07-28
design: terminal
---

# 9 commands to triage a failing pod

At 03:00 a pod is not serving and the dashboard shows one red cell. Three tabs, nine commands, in the order that avoids guessing.

## Quick reference

### What is the phase?

```bash
# phase, restarts and node
kubectl get pod api-7d9f -n prod -o wide
# the Events block at the end
kubectl describe pod api-7d9f -n prod
# spec against status
kubectl get pod api-7d9f -n prod -o yaml
```

### What did it say?

```bash
# only a restarted container has logs
kubectl logs api-7d9f -n prod --previous
# one container, thirty lines
kubectl logs api-7d9f -n prod -c app --tail=30
# every pod of one label
kubectl logs -n prod -l app=api --tail=20
```

### Is the node healthy?

```bash
# conditions and allocatable
kubectl describe node ip-10-0-12-44
# usage against allocatable
kubectl top node ip-10-0-12-44
# evictions across the cluster
kubectl get events -A --field-selector reason=Evicted
```

## Explained

### Look

Start with the phase. The phase is the first fact because it decides which tab can help. kubectl get pod -o wide adds restarts and the node; describe pod ends with the Events block, which names FailedScheduling, a probe failure or a backoff. kubectl get pod -o yaml shows the spec against the status, where a missing claim or a wrong image appears.

### Logs

Logs only exist once a container has run. `--previous` reads the container that died; -c selects one container; -l app=api merges every pod of a label. If the container never started, the log command returns a waiting error; that is a clue, not a broken command.

### Node

If the pod looks fine, check the node. describe node lists conditions and allocatable; top node shows usage; get events `--field-selector reason=Evicted` finds the pods that were pushed out. The field selector keeps the list short; -o wide adds the source node, which is the one to inspect. If the node is healthy, the pod is the problem.

> **The honest caveat:** `kubectl logs --previous` fails when the container never started, and kubectl top needs metrics-server. Without metrics-server, describe still shows the conditions.

> **The lesson:** logs are the pod's side of the story.

## In one line

> **Logs are the pod's side of the story.** The pod reports a symptom; the event names the cause.

**Try it**

```bash
kubectl describe pod api-7d9f -n prod | tail -15
```
