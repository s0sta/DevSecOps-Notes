---
id: p228
title: "5 GitOps mistakes and the fix for each"
slug: 5-gitops-mistakes-and-the-fix-for-each
sections: [devsecops]
topic: "GitOps & Helm"
tags: [GitOps, ArgoCD, Kubernetes, DevSecOps, SRE]
source: "LinkedIn post P228 · Platform series"
linkedin_date: 2028-03-12
design: dontdo
---

# 5 GitOps mistakes and the fix for each

GitOps fails in the same five ways in almost every cluster I have seen. None is exotic, and all are fixable before the next merge.

## Quick reference

**1.** ❌ **Hand edits in the cluster** — Self-heal reverts them, or worse, they survive until the next sync.  
✅ **Every change through Git** — A pull request is the review, the record and the rollback point.

**2.** ❌ **Deploying the :latest tag** — A rollback replays the tag, not the bits it pointed at that day.  
✅ **Pin the image digest** — A digest cannot move, so history and rollback mean something.

**3.** ❌ **Prune enabled by default** — One deleted manifest can take a database or a namespace with it.  
✅ **Prune after an inventory** — List what will be deleted, then enable prune deliberately.

**4.** ❌ **Secrets committed to Git** — Git history keeps the secret long after the file is deleted.  
✅ **Sealed Secrets or SOPS** — The encrypted value is safe to commit; the key lives in the cluster.

**5.** ❌ **Auto-sync with no rollback** — A bad commit reaches production with no human and no way back.  
✅ **Test rollback first** — argocd app rollback must work before you hand over the keys.

## Explained

### The mistakes

1. **Hand edits.** kubectl edit at midnight is the oldest habit in operations. With self-heal on it is reverted; with self-heal off it survives until the next sync. Either way Git no longer describes production. Every change goes through a pull request, even the urgent one.

2. **The :latest tag.** It looks convenient until a rollback replays the tag and pulls whatever latest means today. Pin the digest. Then history and rollback point at the exact bits that ran.

3. **Prune, blind.** prune: true deletes every tracked resource that is no longer in Git, including the database someone removed from a chart by accident. Run a diff, list what will go, then enable it.

4. **Secrets in Git.** Deleting a secret from Git does not delete it from history or from every clone. Use Sealed Secrets, SOPS or External Secrets, and keep the key out of the repo.

5. **Auto-sync, no rollback.** The commit reaches production with no human and no way back. Run argocd app rollback once before enabling auto-sync, not during the incident.

### The common thread

> **The lesson:** each mistake removes a review, a pin or a way back. GitOps is not safe because it is automatic; it is safe when those three survive.

> **The honest caveat:** self-heal will also revert the fix you apply by hand during an incident, so know how to pause auto-sync before you need to.

## In one line

> **Automate the deploy, not the mistake.** If a change did not come through a pull request, it is drift.

**Test rollback now**

```bash
argocd app rollback api 3
```
