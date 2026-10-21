---
id: p437
title: "9 checks for a reproducible build"
slug: 9-checks-for-a-reproducible-build
sections: [devsecops]
topic: "Release & build engineering"
tags: [BuildSystems, DevOps, CICD, ReproducibleBuilds, Security]
source: "LinkedIn post P437 · DevOps series"
linkedin_date: 2029-07-12
design: checklist
---

# 9 checks for a reproducible build

A reproducible build is not a tool you install. It is nine properties of the inputs, the toolchain and the output.

## Quick reference

### Inputs

- **Lockfile is committed** — npm ci, not npm install
- **Base image is pinned** — tag or digest, never latest
- **Build args are declared** — no hidden env in CI

### Toolchain

- **Compiler version is pinned** — same in CI and locally
- **Build runs in a container** — one image, every runner
- **Timestamps normalised** — `set SOURCE_DATE_EPOCH`

### Output

- **Artifact hash is recorded** — `sha256sum release.tar`
- **Image digest is signed** — `cosign sign <digest>`
- **Rebuild is byte-identical** — diff two builds

## Explained

### Inputs

Commit the lockfile and install from it: npm ci rather than npm install, pip install with hashes. Pin the base image by tag, or better by digest, because latest moves under you. Declare every build argument, so a hidden environment variable in CI cannot change the result. A lockfile regenerated on every install is not a lockfile; it is a suggestion.

### Toolchain

Pin the compiler version in the repository, not on the runner: a .tool-versions file, a container image, a wrapper script. Build inside that container, so the laptop and CI run the same binaries. Normalise timestamps with SOURCE_DATE_EPOCH, the reproducible-builds convention, so archives do not differ by the second.

### Output

Record a hash of every artifact: `sha256sum release.tar` gives the next stage something to verify. Sign the image digest with cosign, so a deploy can verify the bits. Rebuild twice and diff the results. If they differ, one build is lying about its inputs.

> **The honest caveat:** bit-for-bit is not always reachable. Compilers embed paths and build IDs, and a signed image carries a timestamp, so reproducible often means every difference is explained rather than absent.

> **The lesson:** reproducibility is a property you check, not a flag you set.

## In one line

> **Same input, same output.** If two builds disagree, one is lying about its inputs.

**Hash the output**

```bash
sha256sum dist/*.tar.gz
```
