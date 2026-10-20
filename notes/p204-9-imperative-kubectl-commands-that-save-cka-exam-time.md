---
id: p204
title: "9 imperative kubectl commands that save CKA exam time"
slug: 9-imperative-kubectl-commands-that-save-cka-exam-time
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CKA, DevOps, CloudNative, CLI]
source: "LinkedIn post P204 · Cloud / DevSecOps series"
linkedin_date: 2028-01-16
design: terminal
---

# 9 imperative kubectl commands that save CKA exam time

The CKA is hands-on and timed, so speed matters. Writing YAML from scratch is slow; generating it with imperative commands is fast. Nine commands that save minutes in the exam and in real work.

## Quick reference

### Make objects in one line

```bash
# a pod, instantly
kubectl run nginx --image=nginx
# a deployment with replicas
kubectl create deploy web --image=nginx --replicas=3
# a service in front of it
kubectl expose deploy web --port=80
```

### Let kubectl write the YAML

```bash
# print the YAML instead of creating it
kubectl run nginx --image=nginx --dry-run=client -o yaml
# save it, edit it, then apply
kubectl create deploy web --image=nginx --dry-run=client -o yaml > web.yaml
# apply your edited version
kubectl apply -f web.yaml
```

### Scale, update, roll back

```bash
# change replica count live
kubectl scale deploy web --replicas=5
# roll out a new image version
kubectl set image deploy/web nginx=nginx:1.27
# back to the previous version
kubectl rollout undo deploy/web
```

## Explained

### Make objects in one line

`kubectl run nginx --image=nginx` creates a pod instantly.  
`kubectl create deploy web --image=nginx --replicas=3` creates a deployment with replicas, the normal way to run something.  
`kubectl expose deploy web --port=80` puts a service in front of it, so other pods can reach it by name.

### Let kubectl write the YAML

`kubectl run nginx --image=nginx --dry-run=client -o yaml` prints the YAML instead of creating anything. This is the single biggest time-saver: let kubectl generate a correct skeleton.  
Redirect it to a file, edit the few fields you need, and `kubectl apply -f web.yaml`. Far faster and less error-prone than typing apiVersion and kind by hand.

### Change fast

`kubectl scale deploy web --replicas=5` changes the replica count live.  
`kubectl set image deploy/web nginx=nginx:1.27` rolls out a new image version, triggering a rolling update.  
`kubectl rollout undo deploy/web` returns to the previous version in seconds, the fastest fix for a bad deploy.

The exam tip that applies everywhere: do not write YAML from a blank file. Generate it with `--dry-run=client -o yaml`, then edit. Also set an alias (alias k=kubectl) and learn kubectl explain for field names, since the docs are allowed in the exam.

## In one line

> **Generate it, don't type it.** `--dry-run=client -o yaml` is the CKA time-saver.

**Try it**

```bash
kubectl run p --image=nginx --dry-run=client -o yaml
```
