---
id: p317
title: "The GPU and Kubernetes cheat sheet"
slug: the-gpu-and-kubernetes-cheat-sheet
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [GPU, Kubernetes, DevOps, SRE, CheatSheet]
source: "LinkedIn post P317 · Visual series"
linkedin_date: 2028-10-05
design: cheatsheet
---

# The GPU and Kubernetes cheat sheet

A GPU pod stops training at 2 a.m. and the dashboard says everything is healthy. The commands that answer the question are four views of the same stack.

## Quick reference

### GPUs

```bash
nvidia-smi
nvidia-smi -L
nvidia-smi topo -m
nvidia-smi --query-gpu=name,memory.used
watch -n 2 nvidia-smi
```

### Nodes

```bash
kubectl describe node gpu-0
kubectl describe node gpu-0 | grep -i gpu
kubectl get node gpu-0 -o yaml
kubectl label node gpu-0 pool=a100
kubectl describe node gpu-0 | tail -20
```

### Pods

```bash
kubectl get pods -A -o wide
kubectl exec -it gpu-pod -- nvidia-smi
kubectl logs -f gpu-pod
kubectl describe pod gpu-pod
kubectl get pod gpu-pod -o yaml
```

### Checks

```bash
kubectl get events -A
kubectl get events -A --watch
kubectl get pods -A | grep Pending
kubectl top pod -A --sort-by=memory
kubectl get events -A -o wide
```

## Explained

### GPUs

Start at the card. `nvidia-smi` shows utilisation, memory and temperature; `nvidia-smi -L` lists the devices; `nvidia-smi topo -m` prints the topology, which tells you whether two GPUs talk over NVLink or PCIe. The query form, `nvidia-smi --query-gpu=name,memory.used`, is the one to remember.

### Nodes

Then the node. `kubectl describe node gpu-0` shows capacity and allocatable, including `nvidia.com/gpu`, and the events at the bottom explain why a card is not schedulable. `kubectl get node gpu-0 -o yaml` is the full record, and `kubectl label node gpu-0 pool=a100` is how you pin a workload to a class of card.

### Pods

Then the workload. `kubectl get pods -A -o wide` shows where it landed. `kubectl exec -it gpu-pod -- nvidia-smi` shows what the container can actually see, and `kubectl logs -f gpu-pod` or `kubectl describe pod gpu-pod` explains a crash or an eviction.

### Checks

Then the cluster. `kubectl get events -A` is the history, and `kubectl get pods -A | grep Pending` finds the jobs waiting for a card. `kubectl top pod -A --sort-by=memory` needs metrics-server, and it catches the pod that is running but not working.

> **The honest caveat:** `nvidia-smi` inside a container shows the cards the container was given, not the whole node, so check the node before you blame the pod.

> **The lesson:** read the card, the node, the pod and the event, in that order.

## In one line

> **The pod is fine. The node is not.** Four views: the card, the node, the pod, the event.

**Start at the card**

```bash
kubectl exec -it gpu-pod -- nvidia-smi
```
