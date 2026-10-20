---
id: p222
title: "9 Argo CD commands for daily GitOps work"
slug: 9-argo-cd-commands-for-daily-gitops-work
sections: [devsecops]
topic: "GitOps & Helm"
tags: [GitOps, ArgoCD, Kubernetes, DevOps, CICD]
source: "LinkedIn post P222 · Platform series"
linkedin_date: 2028-02-27
design: steps
---

# 9 Argo CD commands for daily GitOps work

GitOps means the cluster follows Git, not your terminal history. Argo CD is the tool most teams use to make that true, and its CLI covers the whole loop: sync, inspect, recover.

## Quick reference

### Sync — Send Git to the cluster

```bash
# Apply the Git state now, on demand.
argocd app sync guestbook
# Also delete resources removed from Git.
argocd app sync guestbook --prune
# Block until Synced and Healthy. Use it in CI.
argocd app wait guestbook
```

### Inspect — See before you change

```bash
# Every app with its sync and health status.
argocd app list
# Spec, live state, and what differs.
argocd app get guestbook
# The drift, printed. Nothing is applied.
argocd app diff guestbook
```

### Recover — Go back, safely

```bash
# Deployed revisions, newest first.
argocd app history guestbook
# Reapply revision 3 in seconds.
argocd app rollback guestbook 3
# Stop a sync that is stuck or wrong.
argocd app terminate-op guestbook
```

## Explained

### Sync

argocd app sync applies the Git state now, on demand. It is the same action the controller takes when auto-sync fires.  
`argocd app sync --prune` also deletes resources that were removed from Git. Without it, deleted manifests leave orphans running for ever.  
argocd app wait blocks until the app is Synced and Healthy, which is exactly what you want as the last line of a CI job.

### Inspect

`argocd app list` shows every app with its sync and health status: the fastest overview of a cluster.  
argocd app get shows the spec, the live state, and the differences between them.  
argocd app diff prints the drift without touching the cluster. This is the command to run before a production sync, not after.

### Recover

argocd app history lists the deployed revisions, newest first.  
argocd app rollback redeploys an earlier revision in seconds. It works even when the repo is broken, because it replays what was applied.  
argocd app terminate-op stops a sync that is stuck, or running by mistake.

The habit that matters: diff before sync in production. A sync is a deployment, so treat it like one and look first.

## In one line

> **Sync is a decision, not a habit.** Diff first in production. A sync is a deployment.

**Diff, then sync**

```bash
argocd app diff api
```
