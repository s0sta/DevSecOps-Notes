---
id: p381
title: "DevSecOps terms, decoded"
slug: devsecops-terms-decoded
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [DevSecOps, CyberSecurity, AppSec, CloudNative, ITSecurity]
source: "LinkedIn post P381 · DevSecOps series"
linkedin_date: 2029-03-04
design: reveal
---

# DevSecOps terms, decoded

Every DevSecOps pitch uses the same six words, and half the room nods without knowing which one changes a decision.

## Quick reference

- **Shift left** — Move the check to the pull request, not the release.
- **Threat model** — A short exercise that names what you build and how it can fail.
- **SAST** — Static analysis of your own source, run before the code executes.
- **DAST** — Dynamic testing against a running app, probing it like an attacker.
- **SBOM** — A machine-readable list of every component and version in a build.
- **Security gate** — A pipeline step that stops a release when a threshold is crossed.

## Explained

**The early checks**  
Shift left means moving the check to the pull request. It is a location, not a tool: if the check still runs only before release, nothing shifted.  
A threat model is a short exercise that names what you are building, how it can fail and what you will do about it. It is a meeting with an artefact, not a document you buy.

**The scanners**  
SAST reads your source before it runs and finds patterns: a dangerous call, a missing check. DAST attacks a running app and finds behaviour: a reflected parameter, an open redirect. One sees the code, the other sees the result.

**The list and the gate**  
An SBOM is a machine-readable list of every component and version in a build. It does not make you secure; it makes the next Log4Shell a query instead of a week of grep.  
A security gate is a pipeline step that stops a release when a threshold is crossed. The threshold is the policy; the gate is only the enforcement.

> **The honest caveat:** every one of these can be bought as a product and still fail, because the control is the decision, not the dashboard.

> **The lesson:** learn the words to find the decision each one hides.

## In one line

> **Know the term, own the control.** A word is not a control until someone owns the decision.

**Read the sbom**

```bash
syft . -o spdx-json
```
