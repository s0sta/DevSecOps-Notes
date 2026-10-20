---
id: p293
title: "How a commit reaches production, drawn"
slug: how-a-commit-reaches-production-drawn
sections: [devsecops]
topic: "Git & CI/CD"
tags: [CICD, GitOps, DevOps, Kubernetes, DevSecOps]
source: "LinkedIn post P293 · Visual series"
linkedin_date: 2028-08-10
design: architecture
---

# How a commit reaches production, drawn

A pull request merges at 14:02 and someone asks whether it is live. Between that merge and the answer sit three tiers, and each one hands over a different object.

## Quick reference

- **Source:** Git repository (GIT) · Pull request (PR)
- **Build:** CI runner (CI) · Image registry (REG) · Scan and sign (SCAN)
- **Deploy:** Argo CD (SYNC) · Kubernetes cluster (K8S)

**Request flow:** Git repository → Pull request → CI runner → Image registry → Scan and sign → Argo CD → Kubernetes cluster

## Explained

### Source

The source tier is the Git repository and the pull request. The branch lives in Git, the review lives in the pull request, and branch protection is what makes a second pair of eyes mandatory. The merge is the event everything after it reacts to.

### Build

The build tier is the CI runner, the image registry and the scan-and-sign step. CI runs the tests and builds the image; the registry stores it under a tag and a digest; the scanner reads the pushed digest and cosign signs it. After this tier, the artefact carries evidence of what it is.

### Deploy

The deploy tier is Argo CD and the cluster. Argo CD compares the manifests in Git with the live cluster, shows the diff, and syncs it. The cluster pulls the image by digest, so the manifest decides which bytes run, not a person.

> **The honest caveat:** the chain only holds if the manifest pins the digest. Pin a tag and the same manifest can deploy different bytes next week.

> **The lesson:** production is three handoffs, and each one can swap the artefact. The digest is the only thing that survives all three.

## In one line

> **A commit is not a release.** Production runs a digest, not a branch.

**Trace one commit**

```bash
git log --oneline -1
```
