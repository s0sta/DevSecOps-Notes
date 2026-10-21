---
id: p392
title: "Hardening the CI/CD pipeline, drawn"
slug: hardening-the-ci-cd-pipeline-drawn
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevSecOps, CICD, SupplyChain, CyberSecurity, CloudNative]
source: "LinkedIn post P392 · DevSecOps series"
linkedin_date: 2029-03-29
design: architecture
---

# Hardening the CI/CD pipeline, drawn

A fork pull request reaches your runner in under a minute, and the runner holds the keys. Hardening the pipeline is deciding which tier may hold what.

## Quick reference

- **Trigger:** Pull request (PR) · Fork PR (FORK)
- **Runner:** Isolated runner (CI) · Secrets broker (OIDC)
- **Deploy:** Signed artifact (SIG) · Admission check (GATE)

**Request flow:** Pull request → Isolated runner → Signed artifact → Admission check; Fork PR → Isolated runner

**Around it:** Audit log (LOG)

## Explained

### Three tiers

Trigger. A pull request from a branch in your repository is already trusted. A fork pull request is the untrusted edge: the workflow file comes from your default branch, the code comes from a stranger, and the token is read-only with no secrets.

Runner. Give every job a fresh runner that is destroyed afterwards; a self-hosted runner reused across jobs keeps whatever the last job wrote. The secrets broker mints credentials with OIDC: the job asks GitHub for a signed token, the cloud checks its claims, and returns credentials that expire in an hour by default.

Deploy. The build signs the artifact digest, so the signature covers bytes, not a tag. The admission check verifies that signature and the identity behind it before anything reaches the cluster. The audit log records both decisions.

### Why the boundaries matter

An attacker who owns the runner owns the build, and an attacker who owns the build can sign anything. The runner must not push to production directly: it hands an artifact to a gate that checks a signature it cannot forge.

> **The honest caveat:** signing proves who built the artifact, not that the code is safe. A compromised build signs malicious bytes with valid credentials.

> **The lesson:** put the trust in the artifact and the check, not in the job that ran.

## In one line

> **Trust the artifact, not the job.** A runner is a boundary; treat it like one.

**Check the pin**

```bash
grep -rn 'uses:' .github/
```
