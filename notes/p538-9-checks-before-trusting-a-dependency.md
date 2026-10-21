---
id: p538
title: "9 checks before trusting a dependency"
slug: 9-checks-before-trusting-a-dependency
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SupplyChain, DevSecOps, Security, Python, CICD]
source: "LinkedIn post P538 · PythonSec series"
linkedin_date: 2030-03-05
design: checklist
---

# 9 checks before trusting a dependency

A dependency arrives with a familiar name and a clean scan, and the review stops there. Nine checks in three groups take a few minutes and cover the parts a scanner cannot see.

## Quick reference

### Source

- **Upstream is alive** — commits in last 90 days
- **Name is not a typo** — check the namespace
- **Release is signed** — sigstore or GPG

### Build

- **Version is exact** — == 2.3.0, not >=2.3
- **Lockfile is committed** — hash for every package
- **Install is repeatable** — `pip --require-hashes`

### Runtime

- **SBOM is generated** — `syft dir:. -o cyclonedx`
- **Scan runs on the SBOM** — `grype sbom:sbom.json`
- **Licence is allowed** — `license_audit.py --allow`

## Explained

### Source

Upstream is alive. A package with no commits in a year is not abandoned automatically, but it is a risk you should name. The name is not a typo: check the namespace, because typosquats copy the spelling and the README. The release is signed: sigstore or GPG, and verify the signature against the identity you expect.

### Build

Version is exact. == 2.3.0, not >=2.3, so a rebuild does not quietly move. The lockfile is committed with a hash for every package, including the transitive ones. Install is repeatable: `pip --require-hashes` refuses a package whose hash is not in the file.

### Runtime

The SBOM is generated with `syft dir:. -o cyclonedx`. The scan runs on that SBOM with `grype sbom:sbom.json`, not on a manifest that may disagree with the image. The licence is allowed: run `license_audit.py --allow` against the SBOM, and let the exit code fail the build.

> **The honest caveat:** none of these proves intent. A trusted maintainer can turn hostile, as the xz-utils backdoor showed in 2024, and no checklist sees that coming.

> **The lesson:** trust is a list of checks you can run, not a feeling you can argue.

## In one line

> **Trust is a list of checks.** Nine questions that cost minutes and save a quarter.

**Pin one today**

```bash
pip install pkg==2.3.0
```
