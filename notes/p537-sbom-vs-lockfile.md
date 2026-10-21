---
id: p537
title: "SBOM vs lockfile"
slug: sbom-vs-lockfile
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SBOM, SupplyChain, DevSecOps, Python, CICD]
source: "LinkedIn post P537 · PythonSec series"
linkedin_date: 2030-03-03
design: compare
---

# SBOM vs lockfile

A security review asks what is in the release and what will be installed on the next deploy. Those are two different documents, and teams routinely answer both with whichever file they have open.

## Quick reference

| | **SBOM** | **LOCKFILE** |
|:--|:--|:--|
| What it lists | Every component installed | Every dependency resolved |
| Made by | A scan of the build | A resolve of the manifest |
| Covers | OS and language packages | Language packages only |
| Integrity | Digest of the artefact | Hash of each package |
| Changes when | The build changes | The manifest changes |
| Answers | What shipped? | What will install? |

**SBOM** (What is installed): An inventory of the artefact that was built, down to the OS packages.

```bash
syft dir:. -o cyclonedx-json
```

**LOCKFILE** (What will install): The resolved graph a package manager will reproduce on the next install.

Example: `pip-sync requirements.txt`

- SBOM → evidence of the build.
- Lockfile → a promise before the build.

## Explained

### The two files

An SBOM is generated after the artefact exists. It lists every component that went into the image, including OS packages the language resolver never saw, and it is tied to the image digest. It is evidence of what shipped.

### The lockfile

A lockfile is generated before the artefact exists. The resolver walks the manifest, picks one version for every dependency, records a hash and freezes the graph. The next install reproduces that graph exactly, which is a promise about the future, not a record of the past.

### Where they meet

The lockfile covers language packages. The SBOM covers those plus the base image, the OS libraries and anything copied in at build time. A lockfile can be clean while the image carries a vulnerable OpenSSL, because the base image is outside its view. An SBOM names that OpenSSL; the lockfile keeps the next install honest. You need both, and you need them tied to the same build. The SBOM changes when the build changes; the lockfile changes when someone re-resolves it.

> **The honest caveat:** a lockfile proves what the resolver chose, not that the choice was safe or current, and an SBOM proves what was present, not that it was the only path into the image.

> **The lesson:** the lockfile is a promise, the SBOM is evidence, and the release needs both.

Evidence of the build,  
promise before it.
