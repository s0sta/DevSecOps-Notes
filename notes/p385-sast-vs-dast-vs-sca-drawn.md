---
id: p385
title: "SAST vs DAST vs SCA, drawn"
slug: sast-vs-dast-vs-sca-drawn
sections: [devsecops]
topic: "Application & API security"
tags: [AppSec, SAST, DAST, SCA, CyberSecurity]
source: "LinkedIn post P385 · DevSecOps series"
linkedin_date: 2029-03-13
design: explainer
---

# SAST vs DAST vs SCA, drawn

Three scanners, three views, and most teams buy one and call it coverage. The panels are the questions each tool answers.

## Quick reference

### White box - SAST

- Reads source and builds an abstract syntax tree
- Follows tainted data from a parameter to a sink
- Names the file and line before the merge
- Blind to runtime config and live routes

### Black box - DAST

- Attacks a running app through its own interfaces
- Finds auth gaps, headers, CORS and injection
- No source needed, so any language works
- Cannot point at the line that caused it

### Dependencies - SCA

- Reads lockfiles and SBOMs, not your source
- Matches versions to advisories and licences
- Sees the transitive package four levels down
- Cannot tell whether the vulnerable path runs

### When each runs

- SAST on commit and every pull request
- SCA when the lockfile changes, and nightly
- DAST against staging after each deploy
- All three gate the merge, not a monthly PDF

> **Note:** SAST reads code, DAST attacks a running app, SCA reads the packages both depend on.

## Explained

### White box - SAST

Static analysis reads the source you wrote. It parses the source into an abstract syntax tree, follows tainted data from a request parameter to a sink, and names the file and line before the merge. It is fast enough for every pull request and blind to what exists only at runtime: environment variables, feature flags, routes registered by convention.

### Black box - DAST

Dynamic analysis attacks a running app through its interfaces. It needs no source, so it works on any language or framework, and it finds what a code reader misses: a missing authorisation check, a permissive CORS header and injection. It cannot point at the line that caused it.

### Dependencies - SCA

Software composition analysis reads the lockfile and SBOM, not your source. It matches versions against advisory databases and licence rules, and it alone sees the transitive package four levels down. It cannot tell whether the vulnerable function is ever called.

### When each runs

SAST runs on commit and every pull request. SCA runs when the lockfile changes, and nightly for new advisories. DAST runs against staging after each deploy. All three should gate the same merge, not three PDFs for a monthly meeting.

> **The honest caveat:** a finding from any of them is a lead, not a verdict. Reachability, configuration and exploitability decide whether it is a real risk.

> **The lesson:** the three tools answer different questions, so one of them is never coverage.

## In one line

> **Three lenses, one merge gate.** Different questions, one decision.

**See the panels**

```bash
semgrep --config=auto --error .
```
