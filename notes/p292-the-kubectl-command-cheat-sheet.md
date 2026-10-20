---
id: p292
title: "The kubectl command cheat sheet"
slug: the-kubectl-command-cheat-sheet
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Kubectl, DevOps, CloudNative, SRE]
source: "LinkedIn post P292 · Visual series"
linkedin_date: 2028-08-08
design: cheatsheet
---

# The kubectl command cheat sheet

A pod is restarting, the deploy is stuck, and someone types kubectl get pods for the fourth time. Four groups of commands answer most of that, and none of them needs a dashboard.

## Quick reference

### Inspect

```bash
kubectl get pods -A -o wide
kubectl describe pod api-7d9f
kubectl get deploy api -o yaml
kubectl get events -A --watch
kubectl explain deployment.spec.strategy
```

### Logs

```bash
kubectl logs deploy/api --tail=100
kubectl logs api-7d9f -f
kubectl logs api-7d9f --previous
kubectl logs -l app=api --prefix
kubectl logs api-7d9f --since=1h
```

### Debug

```bash
kubectl exec -it api-7d9f -- sh
kubectl port-forward svc/api 8080:80
kubectl debug -it api-7d9f --image=busybox
kubectl top pod api-7d9f
kubectl run tmp --rm -it --image=busybox
```

### Apply

```bash
kubectl apply -f k8s/
kubectl apply -k overlays/prod
kubectl diff -f k8s/
kubectl rollout status deploy/api
kubectl rollout undo deploy/api
```

## Explained

### Inspect

`kubectl get pods -A -o wide` shows every pod with its node and IP. describe pod api-7d9f gives the events at the bottom, which is usually the reason. get deploy api -o yaml shows what the cluster holds, get events -A `--watch` follows a live incident, and explain settles a field name.

### Logs

`kubectl logs deploy/api --tail=100` is the first look. Add -f to follow, or `--previous` for the container that died. logs -l app=api `--prefix` tags every pod's lines with its name, and `--since=1h` cuts a noisy service to the window that matters.

### Debug

`kubectl exec -it api-7d9f -- sh` gets a shell. port-forward svc/api 8080:80 reaches the service from your laptop. debug -it api-7d9f `--image=busybox` adds a container when the image has no shell. top pod shows usage, and run tmp `--rm -it --image=busybox` gives you a disposable pod inside the cluster network.

### Apply

`kubectl apply -f k8s/` or apply -k overlays/prod. diff -f k8s/ shows the change before you make it, rollout status blocks until it is done, and rollout undo is the way back.

> **The honest caveat:** kubectl debug needs ephemeral containers, beta from 1.23, and kubectl top needs metrics-server; on a stripped cluster both fail rather than degrade.

> **The lesson:** read before you write. Get, describe and logs answer most incidents before any apply.

## In one line

> **Look first. Then apply.** The cluster answers more questions than you ask it.

**Diff before apply**

```bash
kubectl diff -f k8s/
```
