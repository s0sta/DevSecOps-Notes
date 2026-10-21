---
id: p544
title: "Four policy checks that catch most misconfigs"
slug: four-policy-checks-that-catch-most-misconfigs
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [CloudSecurity, Kubernetes, AWS, DevSecOps, PolicyAsCode]
source: "LinkedIn post P544 · PythonSec series"
linkedin_date: 2030-03-19
design: explainer
---

# Four policy checks that catch most misconfigs

A review passes because the Terraform plan is short. The bucket is public, the security group is open, the role is admin and the pod has no limits; the plan was short because nobody read it.

## Quick reference

### Public storage

- A bucket policy with Principal \* and no Condition
- Block Public Access off, or one of its four flags
- An ACL grant to AllUsers or AuthenticatedUsers

### Open ingress

- 0.0.0.0/0 on 22, 3389, 3306 or 5432
- ::/0 on the same ports, often forgotten
- A default security group with an all-traffic rule

### Wildcard IAM

- Action \* and Resource \* in one statement
- s3:\* or iam:\* where one verb was needed
- iam:PassRole with a wildcard resource

### Missing limits

- No resources.limits on any container
- QoS BestEffort: first evicted under pressure
- One pod can starve the node it shares

> **Note:** Four checks, run on every plan and every cluster.

## Explained

### Four checks

Public storage. A bucket policy with Principal \* and no Condition, Block Public Access switched off even for one flag, or an ACL grant to AllUsers or AuthenticatedUsers. Any one is enough to expose the data.

Open ingress. 0.0.0.0/0 or ::/0 on 22, 3389, 3306 or 5432. A default security group with an all-traffic rule is the same finding with a friendlier name.

Wildcard IAM. Action \* with Resource \*, s3:\* where one verb was needed, or iam:PassRole on a wildcard resource. The grant outlives the ticket that asked for it.

Missing limits. No resources.limits on any container puts the pod in the BestEffort class: first to be evicted, and able to starve the node it shares.

### Why these four

Each one is a default that turns a small mistake into an exposure, and each is cheap to check on a plan, a saved JSON dump or a live account. They are not the only checks; they are the four that keep appearing in the same audit.

> **The honest caveat:** each is a candidate, not a verdict. A public website bucket, port 443 and a break-glass admin role are legitimate. The check finds the ones nobody meant.

> **The lesson:** check the four defaults before you argue about the exotic ones.

## In one line

> **Four checks, most misconfigs.** Not every finding is a bug, but every one deserves a look.

**Run the four**

```bash
checkov -d . --compact
```
