---
id: p610
title: "Verify after deploy vs trust the pipeline"
slug: verify-after-deploy-vs-trust-the-pipeline
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevOps, Kubernetes, CICD, SRE, Deployment]
source: "LinkedIn post P610 · PythonFixes series"
linkedin_date: 2030-08-20
design: compare
---

# Verify after deploy vs trust the pipeline

A release turns green and the argument starts: the pipeline already verified it, or someone should look at the pods.

## Quick reference

| | **VERIFY** | **TRUST** |
|:--|:--|:--|
| Question | What is running? | What did we ship? |
| Evidence | Pod digest and age | A green job step |
| Timing | After traffic moves | Before traffic moves |
| Catches | Stale pod, wrong digest | A failed command |
| Misses | A bad smoke assertion | A moved tag |
| Owner | The on-call engineer | The pipeline author |

**VERIFY** (Check what is running): Reads the pods after traffic moves and compares digest, readiness and age.

Example: `deploy_verify.py - release.json`

**TRUST** (Believe the pipeline): Reads the controller's rollout and trusts that the job did what it said.

```bash
kubectl get deploy/api -o yaml
```

- Verify → the pods after the shift.
- Trust → the pipeline before it.

## Explained

### The check

Verify reads the running system after traffic moves. It asks what image digest each pod is on, how many are Ready, and whether any pod is older than the release window. It can catch a stale endpoint, a wrong digest and a rollout that never replaced a pod.

### The trust

Trust reads the pipeline before traffic moves. It asks whether every job step succeeded, whether the rollout controller reports the new revision, and whether the smoke step exited 0. It catches a failed command or a missing step.

### Where they meet

The rows line up the trade. Verify is evidence about now; trust is evidence about intent. Verify catches a wrong digest that trust cannot see when the wrong digest was what the pipeline shipped. Trust catches a broken build that verify never reaches because there is no pod to inspect. Verify misses a silent assertion; trust misses a moved tag. Neither replaces the other, and the owner differs: the pipeline author owns the gate, the on-call engineer owns the check.

Use trust to stop bad releases and verify to prove good ones. The short lines put it plainly: verify the pods after the shift, trust the pipeline before it.

> **The honest caveat:** verify is a snapshot, not a monitor. A pod can be replaced by a bad rollout five minutes after the check passes.

> **The lesson:** the pipeline says what it sent; the pod says what arrived.

The pipeline ships.  
The pod proves it.
