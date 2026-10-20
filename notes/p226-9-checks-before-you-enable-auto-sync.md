---
id: p226
title: "9 checks before you enable auto-sync"
slug: 9-checks-before-you-enable-auto-sync
sections: [devsecops]
topic: "GitOps & Helm"
tags: [GitOps, ArgoCD, Kubernetes, DevSecOps, SRE]
source: "LinkedIn post P226 · Platform series"
linkedin_date: 2028-03-07
design: checklist
---

# 9 checks before you enable auto-sync

Auto-sync is the part of GitOps everyone wants and the part that bites hardest. It means every merge to main reaches the cluster with no human in between, so the checks that used to happen at deploy time have to happen before the merge.

## Quick reference

### Safety

```bash
# Prune is deliberate
prune: true
# Self-heal is on purpose
selfHeal: true
# Rollback works today
argocd app rollback
```

### Access

- **Repo key is read-only** — deploy key: read-only
- **No secrets in Git** — SOPS / Sealed Secrets
- **RBAC is namespace-scoped** — argocd-manager role

### Visibility

```bash
# Failed syncs alert
argocd_app_sync_total
# Health, not just Synced
argocd app wait --health
# Drift is checked nightly
kubectl diff
```

## Explained

### Safety

Prune is a decision. With prune on, removing a manifest deletes the resource. Turn it on deliberately, and know what the first prune will remove.  
Self-heal is a decision too. With selfHeal on, manual cluster edits are reverted within minutes, including the hotfix someone applied at 2 a.m. That is the point, but someone must know it.  
Rollback exists. History and rollback must work before auto-sync is enabled, not discovered afterwards.

### Access

The repo key is read-only. Argo CD only needs to read Git. A write-capable deploy key is a credential an attacker can use to change what you deploy.  
Secrets stay out of Git. SOPS, Sealed Secrets or External Secrets, with the decryption key in the cluster, not the repo.  
Cluster RBAC is scoped. argocd-manager should not be cluster-admin everywhere. Give it what it needs, namespace by namespace.

### Visibility

Failed syncs alert. A failed sync nobody sees is a silent outage, so alert on the Argo CD metrics, not on a dashboard someone remembers to open.  
Health is checked. Synced is not the same as Healthy. An app can be Synced and still CrashLooping.  
Drift is watched. Anything GitOps does not manage still drifts. Run a diff nightly.

> **The lesson:** auto-sync does not remove the checks, it moves them earlier, into the pull request.

## In one line

> **Auto-sync is a promise.** It only holds if a bad commit can be undone in minutes.

**The first check**

```bash
argocd app diff api
```
