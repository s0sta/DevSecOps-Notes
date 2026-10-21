---
id: p384
title: "The SAST, DAST and SCA cheat sheet"
slug: the-sast-dast-and-sca-cheat-sheet
sections: [devsecops]
topic: "Application & API security"
tags: [DevSecOps, AppSec, SAST, DAST, SCA]
source: "LinkedIn post P384 · DevSecOps series"
linkedin_date: 2029-03-11
design: cheatsheet
---

# The SAST, DAST and SCA cheat sheet

A pull request adds a dependency and nobody reads the lockfile. Three scanners in the same pipeline can catch that, and each answers a different question.

## Quick reference

### SAST

```bash
semgrep --config=auto --error .
semgrep --config p/ci --sarif -o s.sarif
bandit -r app/ -ll
gitleaks dir . -v
```

### SCA

```bash
trivy fs --scanners vuln,secret .
npm audit --audit-level=high
npm audit --omit=dev
pip-audit -r requirements.txt
```

### DAST

```bash
nuclei -u https://staging.local
zap-baseline.py -t https://staging.local
nikto -h https://staging.local
sqlmap -u 'https://app/?id=1' --batch
```

### Triage

```bash
jq '.runs[].results | length' s.sarif
jq -r '.runs[].results[].ruleId' s.sarif
sort findings.txt | uniq -c | sort -rn
grype sbom:sbom.json --fail-on critical
```

## Explained

### SAST

SAST reads the code you wrote. `semgrep --config=auto --error .` runs the community rules and fails on a match; `semgrep --config p/ci --sarif -o s.sarif` writes a SARIF file for the code scanning tab. bandit -r app/ -ll reports medium and high Python issues, and `gitleaks dir . -v` looks for hardcoded secrets.

### SCA

SCA reads the code you imported. `trivy fs --scanners vuln,secret .` scans the tree, `npm audit --audit-level=high` fails on high advisories, `npm audit --omit=dev` ignores dev-only packages, and pip-audit -r `requirements.txt` checks a requirements file.

### DAST

DAST attacks the running app. nuclei -u https://staging.local runs the template set against one URL, `zap-baseline.py -t https://staging.local` runs the ZAP baseline scan, nikto -h https://staging.local checks server configuration, and sqlmap -u 'https://app/?id=1' `--batch` tests one parameter without prompting.

### Triage

Triage turns output into a decision. `jq '.runs[].results | length' s.sarif` counts SARIF results, `jq -r '.runs[].results[].ruleId' s.sarif` lists the rules, `sort findings.txt | uniq -c | sort -rn` groups duplicates, and `grype sbom:sbom.json --fail-on critical` gates an SBOM.

> **The honest caveat:** a scanner only reports what its rules know. A clean DAST run against staging says nothing about a route that only exists in production, and a semgrep pass says nothing about business logic.

> **The lesson:** run all three, then triage them in one queue with one owner.

## In one line

> **Scan early, triage once.** A finding without an owner is a log line.

**Fail on high**

```bash
trivy fs --exit-code 1 --severity HIGH .
```
