---
id: p230
title: "GitOps terms, decoded"
slug: gitops-terms-decoded
sections: [devsecops]
topic: "GitOps & Helm"
tags: [GitOps, ArgoCD, Kubernetes, PlatformEngineering, DevOps]
source: "LinkedIn post P230 · Platform series"
linkedin_date: 2028-03-16
design: reveal
---

# GitOps terms, decoded

GitOps arguments usually end with two people meaning different things by the same word. Six terms, decoded, so the next design review is shorter.

## Quick reference

- **drift** — The live cluster no longer matches Git: a hand edit, a deleted resource, a changed image.
- **sync** — Argo CD applies the Git state to the cluster and records the revision it applied.
- **prune** — Deleting live resources that are no longer in Git. Off by default, and dangerous blind.
- **self-heal** — Argo CD reverts manual changes to the resources it tracks, within one reconcile loop.
- **ApplicationSet** — A controller that generates Applications from a template and a generator, one per target.
- **app-of-apps** — One Application whose manifests are other Applications. A tree you manage as a unit.

## Explained

### The basics

drift. The live cluster no longer matches Git: a hand edit, a deleted resource, a changed image. Some drift is invisible until a diff runs. A diff is the only reliable way to see it.  
sync. Argo CD applies the Git state to the cluster and records the revision it applied. Synced means the diff is empty, nothing more.  
prune. Deleting live resources that are no longer in Git. Off by default, and dangerous when it is turned on without a look.  
self-heal. Argo CD reverts manual changes to the resources it tracks, usually within one reconciliation loop. It is not a rollback; it restores what Git already says.

### At scale

ApplicationSet. A controller that generates Applications from a template and a generator: one per cluster, per pull request or per tenant.  
app-of-apps. One Application whose manifests are other Applications. A tree you manage as a unit, instead of a list you maintain by hand.

> **The lesson:** the vocabulary is simple; the defaults are where the arguments live. Most disagreements are about prune, self-heal and who owns the generated apps. Ask which one each person means before the argument starts.

> **The honest caveat:** self-heal only touches resources Argo CD tracks. Anything created outside the app is invisible to it, and stays until someone looks.

## In one line

> **Learn the words, read the diff.** Most GitOps arguments are two definitions of the same term.

**The first term**

```bash
argocd app diff api
```
