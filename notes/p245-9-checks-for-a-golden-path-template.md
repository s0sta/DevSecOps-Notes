---
id: p245
title: "9 checks for a golden-path template"
slug: 9-checks-for-a-golden-path-template
sections: [devsecops]
topic: "Platform engineering"
tags: [PlatformEngineering, DevOps, Kubernetes, CICD, DevSecOps]
source: "LinkedIn post P245 · Platform series"
linkedin_date: 2028-04-20
design: checklist
---

# 9 checks for a golden-path template

Every platform team promises a golden path. Most ship a template repo and a wiki page, then wonder why teams copy the old service. A golden path is nine checks, not a folder.

## Quick reference

### Build

- **Tests run from day one** — `make test` in CI
- **Dependencies are pinned** — lockfile committed
- **Pipeline is included** — CI config in the repo

### Ship

- **Security scan is wired** — Trivy fails on critical
- **Deploy path is real** — staging then production
- **Rollback is tested** — one command, run once

### Own

- **Observability is built in** — metrics, logs, traces
- **Docs live with the code** — README plus a runbook
- **An owner is named** — team in CODEOWNERS

## Explained

### Build

Tests run from day one. The template ships a test target that CI calls, so a new service cannot start with zero tests.  
Dependencies are pinned. A lockfile is committed and CI installs from it, so two builds a week apart match.  
The pipeline is included. The CI config lives in the template, not in a platform ticket. The first push runs lint, test and build.

### Ship

A security scan is wired. Trivy or Grype fails the build on a fixable critical CVE. Scanning after deploy is an audit, not a gate.  
The deploy path is real. Staging and production manifests exist, and the first deploy uses the same Argo CD app as every later one.  
Rollback is documented and tested. One command returns the previous version, and someone has run it before an incident.

### Own

Observability is built in. Metrics, logs and traces are exported from the first commit, not added after an outage.  
Docs live with the code. README, runbook and architecture note sit in the repo and are reviewed with it.  
An owner is named. CODEOWNERS points at a team, and the catalog shows the same team.

> **The lesson:** a golden path is a product, and these nine checks are its acceptance test. The honest caveat: a template nobody maintains becomes a trap, so version it and track adoption.

## In one line

> **The path must be faster than the detour.** Nine checks turn a template into a product teams choose.

**Test the template**

```bash
make test
```
