---
id: p649
title: "Four deploy failures"
slug: four-deploy-failures
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevOps, SRE, Kubernetes, CICD, Bash]
source: "LinkedIn post P649 · ShellSec series"
linkedin_date: 2030-11-19
design: explainer
---

# Four deploy failures

Four failures account for most bad deploys, and none of them is exotic. Each one is a check somebody skipped, and each one is cheaper to catch before the rollout than after it.

## Quick reference

### Wrong context

- The runner kept a kubeconfig from the last job.
- Production manifests land on a staging cluster.
- Every health check passes, on the wrong cluster.

### Stale image

- The tag was rebuilt; the name never changed.
- A node reuses the image it already pulled.
- The pod is Ready and runs the previous code.

### Failed smoke

- Health returns 200 while checkout returns 500.
- One retry hides a backend that flaps.
- The pipeline never calls a paying endpoint.

### No rollback

- revisionHistoryLimit: 0 deleted the undo.
- The previous image was pruned from the registry.
- A migration moved the schema forward.

> **Note:** Each one is cheaper to catch before the rollout than after it.

## Explained

### Wrong context

The runner keeps the kubeconfig from the previous job, or someone runs the prod manifest without switching. The release lands on staging, passes every health check, and production stays on the old version. The context check is first because it decides which cluster answers every later question.

### Stale image

The tag v2 is rebuilt, the name never changes, and a node reuses the image it already pulled. The pod reports Ready while running the previous code. A digest pin is the only reference that cannot be silently rewritten.

### Failed smoke

Health returns 200 because the process is listening; checkout returns 500 because a dependency is not configured. One retry hides a backend that flaps. A smoke test has to assert a status and a body on the endpoint that earns money.

### No rollback

revisionHistoryLimit was set to 0 to keep the cluster tidy, the previous image was pruned from the registry, or a migration moved the schema forward and the old code cannot read it. An undo needs a target, an image and a compatible schema.

> **The honest caveat:** these four checks do not cover a bad migration or a slow leak, which is why the gate is a floor, not a ceiling.

> **The lesson:** deploy failures are check failures that arrived late.

## In one line

> **None of these are surprises.** Each one is a check that did not run.

**The first check**

```bash
kubectl config current-context
```
