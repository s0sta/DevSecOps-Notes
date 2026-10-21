---
id: p450
title: "Quiz: 3 environment questions"
slug: quiz-3-environment-questions
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, SRE, Environments, CICD, CloudNative]
source: "LinkedIn post P450 · DevOps series"
linkedin_date: 2029-08-12
design: quiz
---

# Quiz: 3 environment questions

Three questions separate an environment you trust from one you hope is fine. Answer before the reveal, then check the question that caught you.

## Quick reference

**Q1. Why must staging never share the production secrets?**

- a) A leak there becomes a prod leak
- b) Staging is too slow for real keys
- c) The values would not parse

> **Answer:** a) A leak there becomes a prod leak. A shared secret collapses the boundary: a copied .env or a weaker staging host hands an attacker production access. Scope and rotate each secret per environment.

**Q2. What must a preview environment destroy when its pull request closes?**

- a) The namespace and its data
- b) Only the preview URL
- c) Nothing, to keep it warm

> **Answer:** a) The namespace and its data. The namespace carries the deployment, service, ingress, secrets and volumes. A preview is a lease, so the close ends it; a sweeper catches missed webhooks.

**Q3. Why is environment drift invisible without a baseline?**

- a) Nothing records what correct was
- b) Drift only happens at night
- c) Baselines slow the deploy

> **Answer:** a) Nothing records what correct was. Drift is a difference, so it needs a comparison: a manifest, a saved plan or a snapshot. Without one, whatever is running becomes the definition of correct.

## Explained

### The boundary

Why must staging never share production secrets? Because the boundary is the point. A copied .env, a debug log or a weaker staging host turns a staging compromise into a production one. Scope each secret to one environment, rotate it there, and give staging its own credentials with no production rights.

### The lease

What must a preview environment destroy when its pull request closes? The namespace and its data: deployment, service, ingress, secrets, volumes and the database rows. If the database lives outside the cluster, the teardown deletes its rows as well. A preview is a lease, not a server. Delete it on close, and run a scheduled sweeper for the webhooks that never arrive.

### The baseline

Why is drift invisible without a baseline? Because drift is a difference, and a difference needs two sides. Without a manifest, a saved plan or a snapshot, whatever is running becomes the definition of correct. The first step of any drift check is to record what you expect.

> **The honest caveat:** a baseline is only useful if it is current. A snapshot from six months ago records a state nobody wants any more, and every diff against it will be noise.

> **The lesson:** parity, cleanup and a baseline are the three habits behind every calm environment.

## In one line

> **A baseline is how drift shows.** Three questions, one habit: compare before you trust.

**Snapshot it**

```bash
terraform plan -out=tfplan
```
