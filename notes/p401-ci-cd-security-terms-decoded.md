---
id: p401
title: "CI/CD security terms, decoded"
slug: ci-cd-security-terms-decoded
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevSecOps, CICD, CyberSecurity, CloudNative, AppSec]
source: "LinkedIn post P401 · DevSecOps series"
linkedin_date: 2029-04-19
design: reveal
---

# CI/CD security terms, decoded

Six terms come up in every pipeline security review, and each one is a control you can test.

## Quick reference

- **Runner isolation** — A fresh, single-use runner per job, so nothing a job writes survives into the next one.
- **OIDC** — A job swaps a signed GitHub token for short-lived cloud credentials. No stored key.
- **Pinning** — Referencing an action by its full 40-character commit SHA, because tags can move.
- **Provenance** — A signed record of where and how an artifact was built, checkable before deploy.
- **Cache poisoning** — Seeding a cache entry that a more privileged job later restores and trusts.
- **Least privilege** — A permissions: block that grants one job only the scopes it needs.

## Explained

### Identity

Runner isolation. A fresh, single-use runner for every job. On self-hosted runners that is a configuration choice, and a runner reused across jobs carries the last job's files and credentials into the next one.

OIDC. The job asks GitHub for a signed token, presents it to the cloud, and receives temporary credentials. The cloud checks the issuer, the audience and the subject claim. No long-lived key is stored.

### Supply chain

Pinning. An action referenced by a full 40-character commit SHA cannot be moved. A tag can: the maintainer, or an attacker with the maintainer's account, can point v4 at new code tomorrow.

Provenance. A signed record of what was built, where, from which commit, by which workflow. It answers what a signature cannot: was this built by the pipeline I trust?

Cache poisoning. Seeding a cache entry that a more privileged job later restores and trusts. The defence is to separate cache scopes and never restore a cache into a job that holds secrets.

### Permission

Least privilege. A permissions: block that starts at read-all and grants one job the one scope it needs. The token is the pipeline's identity; every extra scope is a door.

> **The honest caveat:** a vocabulary is not a control. Isolation means nothing without a test that proves the runner is fresh, and least privilege means nothing without a policy that fails the build.

> **The lesson:** name the control, then write the check that proves it.

## In one line

> **Name the control, then check it.** A term you cannot test is a term you cannot enforce.

**List the scopes**

```bash
grep -A2 'permissions:' .github/
```
