---
id: p395
title: "Four ways a CI pipeline leaks"
slug: four-ways-a-ci-pipeline-leaks
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevSecOps, CICD, CyberSecurity, CloudNative, AppSec]
source: "LinkedIn post P395 · DevSecOps series"
linkedin_date: 2029-04-05
design: explainer
---

# Four ways a CI pipeline leaks

A pipeline leak rarely looks like an attack. It looks like a workflow that echoes a variable, or a token with one scope too many.

## Quick reference

### Secrets in logs

- echo `$TOKEN` writes it to a log anyone can read
- Masking hides the exact string, not a base64 copy
- Deleting the run does not delete the download

### Fork pull requests

- pull_request_target runs the base workflow with secrets
- It is safe until a step runs the fork's code
- Checkout now needs allow-unsafe-pr-checkout

### Cache poisoning

- A cache is restored, not verified, by the next job
- GitHub made default-branch cache writes read-only
- Self-hosted and package caches still cross lines

### Over-privileged token

- The default token can write contents in old repos
- Set permissions: read-all, then grant one scope
- A write token can push a tag or edit a release

> **Note:** Every leak is a permission someone did not need.

## Explained

### Secrets in logs

A step prints an environment variable and the value lands in a log anyone with repository access can download. GitHub masks registered secrets, but only the exact string, so a base64 copy goes through. Deleting the run does not delete the copy someone fetched.

### Fork pull requests

pull_request_target runs the workflow from your default branch and gives it the base repository's token and secrets. That is safe until a step checks out the fork's head and runs it. The workflow file is yours; the Makefile it runs is not. GitHub now requires allow-unsafe-pr-checkout before checkout fetches a fork head.

### Cache poisoning

A cache is restored, not verified, so a job that can write an entry can hand the next job a tampered archive under a key it trusts. GitHub made default-branch cache writes read-only for untrusted triggers in June 2026; self-hosted and package caches still cross lines.

### Over-privileged token

A workflow with contents: write can push a commit or move a tag; actions: write can delete artifacts and caches. permissions: read-all at the top, one scope per job, removes most of that reach.

> **The honest caveat:** these are defaults, not exotic bugs, and a scanner that greps only for pull_request_target misses the workflow that fetches fork code with git.

> **The lesson:** every leak is a permission someone did not need.

## In one line

> **The pipeline has the keys.** The pull request has the vote. Never give it the keys.

**Read the trigger**

```bash
grep -rn 'pull_request_target' .github/
```
