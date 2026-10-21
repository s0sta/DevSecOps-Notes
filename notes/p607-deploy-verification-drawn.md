---
id: p607
title: "Deploy verification, drawn"
slug: deploy-verification-drawn
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevOps, Kubernetes, CICD, Deployment, SRE]
source: "LinkedIn post P607 · PythonFixes series"
linkedin_date: 2030-08-13
design: architecture
---

# Deploy verification, drawn

A release passes every pipeline stage and still serves the old code, because the stage checked a tag and the cluster pulled a different digest. The drawing splits the release into the three places where that can be caught.

## Quick reference

- **Build:** Artifact (ART) · Image digest (SHA)
- **Verify:** Manifest check (MAN) · Smoke test (SMK)
- **Ship:** Traffic shift (TRF) · Watch window (WCH)

**Request flow:** Artifact → Manifest check → Smoke test → Traffic shift → Watch window; Image digest → Manifest check

**Around it:** Release record (REL) · Exit code (EXIT)

## Explained

### Build

The first tier is the artifact and its digest. The build produces the file, hashes it and records the digest that will be deployed. An artifact without a digest is a name, and a name can point somewhere else tomorrow.

### Verify

The second tier is the manifest check and the smoke test. The manifest check compares the artifact on disk with path, size and sha256. The smoke test sends one request that only the new release can answer, then asserts the value. A check that runs but asserts nothing is a green light wired to nothing.

### Ship

The third tier is the traffic shift and the watch window. Move a share of traffic, watch error rate and latency against the baseline you recorded before the shift. A strip below the tiers holds the release record and the exit code.

The fix is to make each tier produce evidence: a digest, a manifest result, an asserted response, a watched metric. Prevention is refusing to move traffic until the previous tier has written its evidence.

> **The honest caveat:** this is a model, not an implementation. Traffic may move at the ingress, the service mesh or DNS, and a watch window without a baseline is just waiting.

> **The lesson:** a deploy is a chain of evidence, and the last link is the running pod.

## In one line

> **Built, verified, then shipped.** Three tiers, and a check you can fail at each one.

**Check the digest:** crane digest ghcr.io/acme/api:v2
