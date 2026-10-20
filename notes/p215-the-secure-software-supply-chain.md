---
id: p215
title: "The secure software supply chain"
slug: the-secure-software-supply-chain
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [DevSecOps, SupplyChainSecurity, Kubernetes, CICD, CloudNative]
source: "LinkedIn post P215 · Cloud / DevSecOps series"
linkedin_date: 2028-02-10
design: pipeline
---

# The secure software supply chain

Supply-chain security is 20 percent of the CKS and the fastest-growing area of DevSecOps, because the biggest recent breaches came not from the app but from the pipeline that built it. The defence is a chain where every step proves the next can trust it.

## Quick reference

1. **Write & commit code** — It all starts in git, reviewed and versioned. · `source`
2. **Build the image** — From a trusted, pinned base image, in CI. · *build*
3. **Scan for CVEs** — Trivy fails the build on critical vulnerabilities. · *scan*
4. **Sign the image** — cosign signs it, so its origin is provable. · *sign*
5. **Admission check** — The cluster rejects any image that is unsigned or unscanned. · *verify*
6. **Run with least privilege** — Non-root, read-only filesystem, dropped capabilities. · *run*

## Explained

### Write and commit code

It starts in git: reviewed, versioned, with no secrets committed. If the source is not trustworthy, nothing after it is.

### Build the image

Build in CI from a trusted, pinned base image, not latest. Pinning a digest means you get the exact bytes you tested, not whatever was pushed since.

### Scan for CVEs

Trivy scans the built image for known vulnerabilities and the pipeline fails on criticals. This is the shift-left gate: catch it before it ships, not in production.

### Sign the image

cosign signs the image so its origin is provable. A signature answers the question an attacker hates: did this image really come from our pipeline, unchanged?

### Admission check

An admission controller in the cluster rejects any image that is unsigned or unscanned. This is the enforcement point. Policy stops being a document and becomes a gate.

### Run with least privilege

Finally the pod runs non-root, with a read-only root filesystem and dropped Linux capabilities, so even a compromised container can do little.

Each stage assumes the previous one could be attacked, and verifies instead of trusting. That is the whole idea: provenance you can check at every hop.

## In one line

> **Trust nothing unproven.** A supply-chain attack hides in a step you did not check.

**Add one gate:** scan images in CI before they ever reach the registry
