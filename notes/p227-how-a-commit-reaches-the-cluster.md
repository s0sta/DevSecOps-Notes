---
id: p227
title: "How a commit reaches the cluster"
slug: how-a-commit-reaches-the-cluster
sections: [devsecops]
topic: "GitOps & Helm"
tags: [GitOps, ArgoCD, Kubernetes, CICD, DevOps]
source: "LinkedIn post P227 · Platform series"
linkedin_date: 2028-03-09
design: pipeline
---

# How a commit reaches the cluster

A merge to main passes CI, and four minutes later the cluster runs a different image. The path between those two moments is short, mostly automatic, and worth knowing end to end.

## Quick reference

1. **A commit lands on main** — The merge to main is the only trigger that matters. · `git`
2. **CI builds an image** — Tests pass, then the image is tagged with the commit SHA. · *ci*
3. **Scan and sign** — Trivy checks for CVEs; cosign signs the digest. · *scan+sign*
4. **Manifest is updated** — CI writes the new tag into the manifests repo. · *manifest*
5. **Argo CD detects it** — It polls Git every three minutes, or gets a webhook. · `argocd`
6. **Apply and check health** — The diff is applied, then health gates the result. · *health*

## Explained

### The pipeline

1. **A commit is pushed.** The merge to main is the only trigger that matters.
   \2. CI builds an image. Tests run, then a multi-stage build tags it with the commit SHA.
   \3. Scan and sign. Trivy checks the image for CVEs, and cosign signs the digest.
   \4. The manifest is updated. CI writes the new tag into the manifests repo, usually as a pull request.
   \5. Argo CD detects it. It polls Git every three minutes by default, or receives a webhook, then computes the diff.
   \6. Apply and check health. Argo CD applies the diff and waits for health before the sync is called done.

### Where it breaks

Most failures are not in the cluster. A mutable tag means CI ships something different from what it tested. A manifest repo without review means the wrong change is already in Git. An app that reports Synced while pods CrashLoop is a health check nobody read.

### The habit

The habit that matters: move the image digest, not the tag, between stages. A digest cannot be repointed, so every step above can be audited afterwards.

> **The honest caveat:** this chain is only as strong as the manifest repo's permissions. If CI can push straight to main there, the review step is decoration.

## In one line

> **Git is the source. The cluster is a copy.** Every step after the commit is mechanical and repeatable.

**Watch it happen**

```bash
argocd app get api
```
