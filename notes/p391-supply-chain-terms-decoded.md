---
id: p391
title: "Supply chain terms, decoded"
slug: supply-chain-terms-decoded
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SupplyChain, SLSA, SBOM, DevSecOps, CyberSecurity]
source: "LinkedIn post P391 · DevSecOps series"
linkedin_date: 2029-03-27
design: reveal
---

# Supply chain terms, decoded

Six words do most of the work in supply-chain conversations. Learn what each proves and the sales deck stops sounding like magic.

## Quick reference

- **Provenance** — A record of where and how an artefact was built, tied to a source commit.
- **SBOM** — A machine-readable inventory of every component and version inside a build.
- **Attestation** — A signed statement about a build, a test or a scan, bound to an artefact digest.
- **SLSA** — A build-hardening scale: Build L1 to L3, with L3 the strongest.
- **Typosquatting** — A lookalike package name, one keystroke away from the real one.
- **Dep confusion** — A public package published under an internal name, hoping a resolver picks it.

## Explained

### The build

Provenance is a record of where and how a build ran: the repository, the commit, the builder and the steps. It answers who built this, not whether the code is safe.

An SBOM is a machine-readable inventory of every component and version inside a build, usually SPDX or CycloneDX. It answers what is inside, a question a Dockerfile cannot answer.

An attestation is a signed statement about an artefact, bound to its digest: a build ran, a test passed, a scan found nothing. It answers what was claimed, and by whom.

SLSA's build track is a hardening scale. Build L1 means provenance exists; L2 means a hosted platform signs it; L3 means a hardened platform isolates the build and protects the signing key. It answers how far you can trust the builder.

### The name

Typosquatting is a lookalike name: one letter changed, a hyphen moved, a scope added. It answers whether you installed the package you meant to install.

Dependency confusion publishes a package under an internal name, hoping the resolver prefers the public copy. It answers whether your registry precedence is a control or an accident.

> **The honest caveat:** a signature proves who signed, not that the signed thing is good. Provenance and attestations move trust to the builder; they do not remove it.

> **The lesson:** every term is a question you can ask of an artefact before deploying it.

## In one line

> **Prove the build, not the badge.** A signature is only useful when you know what it covers.

**Verify one image**

```bash
cosign verify --key cosign.pub $IMAGE
```
