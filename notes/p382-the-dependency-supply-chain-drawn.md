---
id: p382
title: "The dependency supply chain, drawn"
slug: the-dependency-supply-chain-drawn
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [DevSecOps, SupplyChain, AppSec, CyberSecurity, SCA]
source: "LinkedIn post P382 · DevSecOps series"
linkedin_date: 2029-03-06
design: architecture
---

# The dependency supply chain, drawn

A package you never chose runs with the permissions of the service that imported it. Between the registry and production it passes seven stops, and the weakest one decides the risk.

## Quick reference

- **Source:** Public registry (PUB) · Private registry (PRIV) · Lockfile (LOCK)
- **Build:** SCA scan (SCA) · SBOM (SBOM)
- **Consume:** Admission check (GATE) · Runtime workload (RUN)

**Request flow:** Public registry → SCA scan → SBOM → Admission check → Runtime workload; Private registry → SCA scan; Lockfile → SCA scan

## Explained

### Source

The first tier is where code enters. The public registry serves open-source packages. The private registry holds the packages your organisation builds and does not publish. The lockfile records the exact version and hash of every fetched package, so the same install reproduces on a laptop, a runner and a container.

### Build

The second tier turns that tree into evidence. The SCA scan reads the lockfile, matches each version against advisory data and flags the ones with known CVEs. The SBOM records every component, including the transitive packages nobody named, so the next question is a query, not an archaeology project.

### Consume

The third tier is where the package finally runs. The admission check refuses an image whose signature or provenance does not match policy. The runtime workload is where the imported code executes with your service account and your network access.

Read the arrows as trust boundaries. Both registries feed the SCA scan, the lockfile feeds it too, and the scan produces the SBOM. The SBOM is what admission checks against, and nothing reaches runtime without crossing that line.

> **The honest caveat:** an SBOM proves what is inside a build, not that any of it is safe, and a lockfile only protects you when CI runs npm ci, not npm install.

> **The lesson:** the supply chain is only as strong as the stop nobody reviews.

## In one line

> **Trust the hash, not the name.** A package is a claim until its hash and its source agree.

**Audit the lockfile**

```bash
python3 lockfile_audit.py package-lock.json
```
