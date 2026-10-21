---
id: p647
title: "The deploy gate, in three tiers"
slug: the-deploy-gate-in-three-tiers
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Bash, DevOps, Kubernetes, CICD, SRE]
source: "LinkedIn post P647 · ShellSec series"
linkedin_date: 2030-11-14
design: architecture
---

# The deploy gate, in three tiers

Every deploy passes through the same three tiers, whether or not anyone drew them. The first decides whether the release is allowed, the second turns five answers into one exit code, and the third changes the cluster and watches it.

## Quick reference

- **Tier 1 · Checks:** Context match (CTX) · Namespace exists (NS) · Previous rollout (DEP) · Alert file (ALRT)
- **Tier 2 · Gate:** Digest pinned (SHA) · Pass or fail (EXIT)
- **Tier 3 · Ship:** Rollout (SET) · Watch 10 min (OBS)

**Request flow:** Context match → Namespace exists → Previous rollout → Alert file → Digest pinned → Pass or fail → Rollout → Watch 10 min

**Around it:** CI runner (RUN) · Registry (IMG) · Pager (PAGE) · Audit log (LOG)

## Explained

### Checks

Four checks run before anything is applied. The context must match the environment the pipeline claims to deploy to. The namespace must exist. The previous rollout must already be healthy, because a second release on top of a broken one hides both failures. The incident flag file must be absent, which is how on-call freezes deploys without editing the pipeline.

### Gate

The digest check sits in the gate tier because it is the last thing that can veto the release: an image pinned by tag is a promise someone can rewrite. The verdict is a single exit code. Zero opens the gate; anything else stops the pipeline before kubectl apply runs.

### Ship

Only then does the rollout start. The gate waits for the Deployment to report healthy, and the watch step holds for ten minutes of error rate and latency, because a rollout that reports success is not the same as a release that works.

> **The honest caveat:** a gate only guards the path that runs it. Anyone with kubectl and permission can go around it, so RBAC still matters.

> **The lesson:** the gate is where a team agrees, in code, what a deploy is allowed to assume.

## In one line

> **Checks decide, the gate enforces.** A gate is the deploy argument, settled in code.

**The first check**

```bash
kubectl config current-context
```
