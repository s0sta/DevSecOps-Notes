---
id: p648
title: "Deployment shell commands"
slug: deployment-shell-commands
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Bash, Kubernetes, DevOps, SRE, CommandLine]
source: "LinkedIn post P648 · ShellSec series"
linkedin_date: 2030-11-17
design: cheatsheet
---

# Deployment shell commands

Deployment work is four blocks of commands: what cluster am I on, what is rolling out, what is it saying, and how do I undo it. The order is not cosmetic. The first block is the one that prevents the expensive mistake.

## Quick reference

### CONTEXT

```bash
kubectl config current-context
kubectl config get-contexts
kubectl config use-context prod-eu
kubectl get ns api -o name
kubectl cluster-info
```

### ROLLOUT

```bash
kubectl rollout status deploy/api
kubectl rollout history deploy/api
kubectl rollout restart deploy/api
kubectl set image deploy/api api=api:v2
kubectl get pods -n api -w
```

### LOGS

```bash
kubectl logs -f deploy/api -n api
kubectl logs --tail=100 deploy/api
kubectl logs -p deploy/api -n api
kubectl describe pod -n api -l app=api
kubectl get events -n api
```

### ROLLBACK

```bash
kubectl rollout undo deploy/api
kubectl rollout undo deploy/api -n api
kubectl rollout status deploy/api -n api
kubectl get rs -n api
kubectl get pods -n api
```

## Explained

### Context

`kubectl config current-context` prints the name the rest of your commands will use. get-contexts lists what is available; use-context switches. get ns proves the namespace exists before you apply into it.

### Rollout

kubectl rollout status blocks until the Deployment is done, and it is the line that should end a pipeline. rollout history lists revisions, restart cycles the pods without a manifest change, set image updates one container, and get pods -w watches the replacements arrive.

### Logs

`kubectl logs -f` follows one Deployment; `--tail=100` gives the last hundred lines without the scroll; -p reads the previous container after a crash. describe pod shows events and exit codes, and get events shows the cluster's own story.

### Rollback

kubectl rollout undo returns to the previous revision; add `--to-revision` N when you know the target. rollout status confirms the undo landed, get rs shows the old ReplicaSets still available, and get pods proves what is running.

> **The honest caveat:** kubectl reads the current context, so every command here is one context switch away from the wrong cluster.

> **The lesson:** type the context check before the command, every time.

## In one line

> **Context first, command second.** Every other block assumes the right cluster.

**Check the context**

```bash
kubectl config current-context
```
