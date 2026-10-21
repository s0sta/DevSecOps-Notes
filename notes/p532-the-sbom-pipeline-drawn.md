---
id: p532
title: "The SBOM pipeline, drawn"
slug: the-sbom-pipeline-drawn
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SBOM, SupplyChain, DevSecOps, Python, CICD]
source: "LinkedIn post P532 · PythonSec series"
linkedin_date: 2030-02-19
design: architecture
---

# The SBOM pipeline, drawn

A base image moves a minor version and 40 packages change underneath you. The build stays green, the audit trail says nothing, and nobody can answer what actually shipped. An SBOM answers that only if it is generated, stored and compared in the same place.

## Quick reference

- **Generate:** Build (BUILD) · syft scan (SBOM)
- **Store:** OCI registry (OCI) · Artefact store (STORE)
- **Diff:** SBOM diff (DIFF) · Policy gate (GATE)

**Request flow:** Build → syft scan → OCI registry → SBOM diff → Policy gate; syft scan → Artefact store

**Around it:** Image digest (DIG) · Exit code (EXIT)

## Explained

### Generate

The scan belongs in the build, not on a laptop. The build produces the image and its digest, then syft reads that artefact and writes CycloneDX JSON listing every package and version. Because the scan runs after the image exists, the list belongs to the bytes that will ship.

### Store

The file goes into the OCI registry beside the image, or into the artefact store the pipeline already uses. Tag it with the image digest, never the branch name. An SBOM nobody can find at 3 a.m. is a document, not evidence.

### Diff

Before the gate, compare the candidate with the SBOM from production. The diff has three outcomes: components added, removed and version-changed. The version change is the one to read, because a patch bump can add a transitive package or remove one that carried a fix. The policy gate reads that diff, and the job exits non-zero when the inventory moved.

> **The honest caveat:** an SBOM is an inventory, not a scan. It tells you what is inside, not whether any of it is vulnerable, and two scanners can produce different component lists for the same image.

> **The lesson:** generate once, store with the digest, and diff every build.

## In one line

> **Generate once, diff every build.** An SBOM that is never compared is a document, not a control.

**Diff two sboms**

```bash
python3 sbom_diff.py old.json new.json
```
