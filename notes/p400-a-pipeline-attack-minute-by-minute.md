---
id: p400
title: "A pipeline attack, minute by minute"
slug: a-pipeline-attack-minute-by-minute
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevSecOps, CICD, CyberSecurity, IncidentResponse, SupplyChain]
source: "LinkedIn post P400 · DevSecOps series"
linkedin_date: 2029-04-17
design: timeline
---

# A pipeline attack, minute by minute

The alert did not fire when the pull request opened. It fired nineteen days later, when someone read a bill.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **0m** | Push to a fork | The attacker forks the repo and opens a pull request. |
| **1m** | Token issued | pull_request_target hands the job a write token and secrets. |
| **2m** | Cache poisoned | A package cache the release build trusts now holds bad bytes. |
| **4m** | Secrets read | The job prints its environment; the log is readable. |
| **6m** | Artifact published | The write token pushes a new image tag to the registry. |
| **19d** | Detection | A bill, an audit log or a scanner finally connects the dots. |

## Explained

### The first minutes

0m. Push to a fork. The attacker forks the repository and opens a pull request from a branch. Nothing looks unusual: a fork, a commit and a green check requested.

1m. Token issued. The workflow uses pull_request_target. It runs from the default branch, so the job receives the base repository's token and its secrets, and the token can write.

2m. Cache poisoned. The job writes an entry into a package cache the release workflow trusts. A later restore unpacks it and treats the contents as its own build output.

### The next minutes

4m. Secrets read. A step prints its environment, or reads a file the token can reach. The run log is readable to anyone with repository access.

6m. Artifact published. The write token pushes a new tag to the registry, or edits a release. The image carries the project's name and a plausible version.

### The detection

19d. Detection. A cloud bill, an audit log or a scanner finally connects the fork to the image. The mean time to detect is measured in weeks because nothing watches the pipeline itself.

> **The honest caveat:** this is a composite of documented cases, and the timings are illustrative. GitHub's 2026 cache and checkout changes close the easiest version, but the chain still runs wherever secrets are reachable.

> **The lesson:** the pipeline is a production system, so alert on it like one.

## In one line

> **Detection is the last step.** The first five happen before anyone looks.

**Read the log**

```bash
gh run view --log
```
