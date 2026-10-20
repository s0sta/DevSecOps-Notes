---
id: p306
title: "The software supply chain, drawn"
slug: the-software-supply-chain-drawn
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [SupplyChain, DevSecOps, CICD, SBOM, CloudNative]
source: "LinkedIn post P306 · Visual series"
linkedin_date: 2028-09-10
design: architecture
---

# The software supply chain, drawn

The build that shipped on Tuesday pulled a package published that morning from an account with no MFA. The miner ran for six hours before anyone looked at egress.

## Quick reference

- **Tier 1 · Source:** Git commit (GIT) · Dependencies (DEP)
- **Tier 2 · Build:** CI pipeline (CI) · SBOM (SBOM) · Signing (SIGN)
- **Tier 3 · Deploy:** Verify signature (VFY) · Admission control (ADMIT) · Runtime monitor (RUN)

**Request flow:** Git commit → Dependencies → CI pipeline → SBOM → Signing → Verify signature → Admission control → Runtime monitor; Git commit → CI pipeline

## Explained

### Source

Every commit is an input, and every dependency is code you did not write. The source tier has two nodes: the git commit and the dependency set. Pin versions, commit the lockfile, and review a new package the way you review a new colleague. A commit is cheap to make and hard to take back.

### Build

The CI pipeline runs on that commit, builds the artefact, writes an SBOM, and signs the result. The three nodes are CI, SBOM and signing. The signature is only worth something if the signing identity belongs to the pipeline, not to a laptop. If the SBOM is written after signing, the signature covers less than you think.

### Deploy

Verification checks the signature against the identity you expect. The admission controller refuses an artefact that fails the check, and the runtime monitor watches what the container does after it starts. Verify, admit, run: three nodes and three chances to stop the same attack. The runtime monitor is the only node that watches behaviour, not metadata.

> **The honest caveat:** signing proves who built the artefact, not that the code is safe. A signed malicious dependency is still malicious.

> **The lesson:** trust the artefact you verified, not the network you built it on.

## In one line

> **Build it, sign it, verify it.** Three tiers, and every artefact carries proof.

**Verify an image**

```bash
cosign verify ghcr.io/acme/api:1.4
```
