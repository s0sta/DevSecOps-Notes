---
id: p598
title: "The kubectl triage cheat sheet"
slug: the-kubectl-triage-cheat-sheet
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, kubectl, SRE, DevOps, CloudNative]
source: "LinkedIn post P598 · PythonFixes series"
linkedin_date: 2030-07-23
design: cheatsheet
---

# The kubectl triage cheat sheet

A failing pod produces more output than any human can read. Four blocks keep the order, and the order matters more than the flags.

## Quick reference

### Pods

```bash
kubectl get pods -A -o wide
kubectl describe pod -n prod api-7d9f
kubectl logs -n prod api-7d9f --previous
kubectl get pod -n prod api-7d9f -o yaml
```

### Events

```bash
kubectl get events -A -w
kubectl get events -A | grep Evicted
kubectl events --for pod/api-7d9f -n prod
kubectl get events -A -o wide
```

### Nodes

```bash
kubectl get nodes -o wide
kubectl describe node ip-10-0-12-44
kubectl top node ip-10-0-12-44
kubectl cordon ip-10-0-12-44
```

### Jobs

```bash
kubectl get jobs -A
kubectl get cronjobs -A
kubectl describe job -n batch nightly-etl
kubectl logs job/nightly-etl -n batch
kubectl create job y --from=cronjob/x
```

## Explained

### Pods

Start with the pod: phase, restarts, node and events. `kubectl get pods -A -o wide` gives the shape; kubectl describe pod prints the Events block at the end. A Pending pod has no logs, so describe comes before logs. `kubectl logs --previous` reads the container that died, and -o yaml shows the spec against the status.

### Events

Events are the cluster's own account. Watch them with `kubectl get events -A -w`; grep Evicted for node pressure; `kubectl events --for` narrows the list to one pod. The newest event is usually the cause; the older ones are the aftermath.

### Nodes

Then the node: conditions, allocatable and current usage. describe node shows MemoryPressure; top node needs metrics-server; cordon stops new pods while you work, but it does not stop the pods already there.

### Jobs

A CronJob that schedules is not a Job that succeeds. `kubectl get jobs -A`, describe job for the backoff reason, logs job/nightly-etl for the last pod, create job `--from=cronjob` to retry by hand. The Job keeps the count; its pods keep the exit codes.

> **The honest caveat:** `kubectl events --for` needs a recent kubectl, and kubectl top needs metrics-server. Without them, describe and the event list still work.

> **The lesson:** read the event, not the dashboard.

## In one line

> **Read the event, not the dashboard.** The cluster writes the reason before you write a theory.

**Describe first**

```bash
kubectl describe pod -n prod api-7d9f
```
