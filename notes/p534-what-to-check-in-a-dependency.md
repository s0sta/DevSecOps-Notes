---
id: p534
title: "What to check in a dependency"
slug: what-to-check-in-a-dependency
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SupplyChain, DevSecOps, SBOM, Security, Python]
source: "LinkedIn post P534 · PythonSec series"
linkedin_date: 2030-02-24
design: explainer
---

# What to check in a dependency

A package arrives in a pull request with a familiar name, a green CI run and a README you remember. Four questions decide whether it belongs in the build.

## Quick reference

### 1. Version

- Pin an exact version, not a range
- Commit the lockfile with hashes
- Ranges resolve differently tomorrow
- Pin the transitive packages too

### 2. Licence

- MIT and Apache-2.0 are permissive, with duties
- GPL-3.0 can reach your own source
- Read the identifier, not the README
- No licence is not permission

### 3. Provenance

- Who published it, and from which commit
- Attestations bind source to digest
- Typosquats copy the name and the README
- Check the namespace, not the logo

### 4. Vulnerabilities

- A CVE list is dated the hour it is made
- Reachability decides what matters
- Scan the SBOM, not just the manifest
- A fix is not always a safe version

> **Note:** Four checks, one pull request, in this order.

## Explained

### Version

Pin an exact version. Commit the lockfile with hashes. A range such as ~=2.0 promises compatibility and delivers whatever the resolver finds: a different tree next month. Pin the transitive packages too, because the one you did not name is the one that changed.

### Licence

MIT and Apache-2.0 are permissive, though Apache-2.0 adds a notice duty and a patent grant. GPL-3.0 can reach your own source if you distribute the combined work. Read the identifier, not the README. A package with no licence is not permission; it is an unanswered question.

### Provenance

Ask who published the artefact and from which commit. A signed attestation binds the source repository to the image digest, so a rebuilt artefact can be checked against the same source. Typosquats copy the name and the README, so check the registry namespace, not the logo.

### Vulnerabilities

A CVE list is dated the hour it is generated. Match it against the SBOM, then ask whether the vulnerable function is reachable from your code. A high score in a package you never call is noise; a medium in the parser that reads user input is not. Upgrading is not automatically safer, because a fix can arrive with a new dependency.

> **The honest caveat:** provenance is only as strong as the ecosystem that signs it, and most packages still ship no attestation.

> **The lesson:** trust is four checks, not one reputation.

## In one line

> **Four checks, not a feeling.** The file records a choice. The build should enforce it.

**Check one package**

```bash
grype sbom:sbom.json
```
