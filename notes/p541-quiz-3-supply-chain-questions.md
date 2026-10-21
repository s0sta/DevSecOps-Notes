---
id: p541
title: "Quiz: 3 supply-chain questions"
slug: quiz-3-supply-chain-questions
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SupplyChain, SBOM, Terraform, DevSecOps, Security]
source: "LinkedIn post P541 · PythonSec series"
linkedin_date: 2030-03-12
design: quiz
---

# Quiz: 3 supply-chain questions

Three questions separate a supply-chain control from a supply-chain document. Answer before the reveal.

## Quick reference

**Q1. Why is an SBOM not a vulnerability scan?**

- a) It lists packages, not CVEs
- b) It only covers containers
- c) It is generated after deploy

> **Answer:** a) It lists packages, not CVEs. An SBOM is an inventory of names, versions and licences. A scanner matches that inventory against advisories. Without it, the file is a manifest, not a finding.

**Q2. What does a lockfile prove?**

- a) That the build passed
- b) That the graph resolved once
- c) That no CVE exists

> **Answer:** b) That the graph resolved once. It records the exact versions and hashes the resolver chose, so the same install reproduces them. It proves what was resolved, not that it is safe or current.

**Q3. Why pin a git module to a SHA, not a branch?**

- a) A branch has no version
- b) A branch can move under you
- c) Terraform rejects branches

> **Answer:** b) A branch can move under you. A branch is a pointer: the next commit changes what runs, with no diff in your repo. A SHA names one tree, so the plan is reproducible and an upgrade is a review.

## Explained

### SBOM versus scan

Question one: why is an SBOM not a vulnerability scan? Because it is an inventory. It lists the components, versions and licences it found, and stops. A scanner takes that list and matches it against advisories, which is where a CVE appears. An SBOM with no scan is a manifest; a scan with no SBOM is a guess about what is installed.

### What a lockfile proves

Question two: what does a lockfile prove? That the resolver ran once and produced a graph, and that a later install can reproduce it from the recorded versions and hashes. It proves the graph, not its safety. A locked package can be three years old, and the lockfile will happily reproduce the vulnerability.

### Branch or SHA

Question three: why pin a git module to a SHA, not a branch? A branch is a pointer that moves. The next commit changes what runs in your account, and your repository shows no diff. A commit SHA names one tree, so a plan is reproducible and an upgrade becomes a reviewable change.

> **The honest caveat:** a SHA can still point at malicious code. Pinning gives you reproducibility and a review point, not trust.

> **The lesson:** a list is not a verdict, and a pin is not a promise of safety.

## In one line

> **A list is not a verdict.** Three questions to close the supply-chain phase.

**Ask the sbom**

```bash
syft dir:. -o cyclonedx-json
```
