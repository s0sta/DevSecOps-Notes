---
id: p393
title: "The CI/CD security cheat sheet"
slug: the-ci-cd-security-cheat-sheet
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevSecOps, CICD, GitHubActions, CyberSecurity, CheatSheet]
source: "LinkedIn post P393 · DevSecOps series"
linkedin_date: 2029-04-01
design: cheatsheet
---

# The CI/CD security cheat sheet

Most CI security work is a grep away. The failures are visible in the workflow files before a runner starts, and four blocks of commands cover the ground.

## Quick reference

### Workflows

```bash
grep -rn 'pull_request_target' .github/
grep -rn 'allow-unsafe' .github/
grep -rn 'uses:.*@v[0-9]' .github/
actionlint .github/workflows/*.yml
zizmor .github/workflows/
```

### Permissions

```bash
grep -rn 'permissions:' .github/
grep -rn 'write-all' .github/
gh api repos/$R/actions/permissions
grep -rn 'GITHUB_TOKEN' .github/
gh api orgs/$O/actions/permissions
```

### Pinning

```bash
grep -rn 'uses:.*@' .github/workflows/
grep -rnE '@(main|master)' .github/
pinact run
ratchet pin .github/workflows/ci.yml
grep -c 'uses:' .github/workflows/*.yml
```

### Secrets

```bash
grep -rn 'secrets\.' .github/workflows/
gh secret list
gh api repos/$R/actions/secrets
gitleaks dir . -v
trufflehog filesystem . --only-verified
```

## Explained

### Workflows

Read the files first. `grep -rn 'pull_request_target' .github/` finds the event that runs with the base repository's token, and `grep -rn 'allow-unsafe' .github/` finds the checkout flag that lets a fork's code into that job. actionlint .github/workflows/\*.yml parses the YAML and catches expressions that would fail at runtime, and zizmor .github/workflows/ reads the same files for security patterns.

### Permissions

`grep -rn 'permissions:' .github/` shows which workflows set them at all; a missing block means the repository default applies. `grep -rn 'write-all' .github/` finds the broadest setting. `gh api repos/$R/actions/permissions` prints the repository policy for R as owner/repo, including whether SHA pinning is required.

### Pinning

`grep -rn 'uses:.*@' .github/workflows/` lists every action reference. A tag like @v4 can be moved; a 40-character SHA cannot. pinact run rewrites the files to SHAs, and ratchet pin .github/workflows/ci.yml does the same for one workflow.

### Secrets

`grep -rn 'secrets\.' .github/workflows/` shows what a workflow can reach. `gh secret list` shows what exists. `gitleaks dir . -v` scans the working tree for committed credentials, and trufflehog filesystem . `--only-verified` checks the hits against the provider.

> **The honest caveat:** a grep proves nothing. It points at a line a human still has to read, and pull_request_target is not always wrong.

> **The lesson:** the cheapest pipeline audit is the one that reads the files before the runner does.

## In one line

> **The files are the evidence.** Read them before the runner does.

**Start with the event**

```bash
grep -rn 'pull_request_target' .github/
```
