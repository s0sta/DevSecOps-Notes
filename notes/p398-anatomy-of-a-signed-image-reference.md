---
id: p398
title: "Anatomy of a signed image reference"
slug: anatomy-of-a-signed-image-reference
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [DevSecOps, Containers, SupplyChain, Kubernetes, CloudNative]
source: "LinkedIn post P398 · DevSecOps series"
linkedin_date: 2029-04-12
design: anatomy
---

# Anatomy of a signed image reference

A Kubernetes manifest says ghcr.io/acme/api:1.4.2, and the cluster may run something else tomorrow, because a tag is a pointer and pointers move.

## Quick reference

```text
ghcr.io/acme/api:1.4.2@sha256:9f2c7b1e
```

| Part | Name | What it means |
|:--|:--|:--|
| `ghcr.io` | Registry | The host that stores the image. Docker Hub is implied when it is omitted. |
| `/acme` | Organisation | The namespace or org that owns the repository. |
| `/api` | Image | The repository name inside that namespace: what you push and pull. |
| `:1.4.2` | Tag | A human label. It can be moved to a new digest at any time. |
| `@sha256:9f2c7b1e` | Digest | The content hash, 64 hex characters. Immutable and verifiable. |

## Explained

### Five parts

Registry. `ghcr.io` is the host. If you write api:1.4.2 with no host, Docker and Kubernetes assume docker.io, so the short form hides where it lives.

Organisation. acme is the namespace or organisation that owns the repository. On GHCR it is usually the GitHub user or org, and access is granted per package.

Image. api is the repository inside that namespace: the name you push to and pull from.

Tag. 1.4.2 is a human label. It is mutable: the same tag can point at a new digest an hour from now, and nothing in the reference records that it moved.

Digest. sha256:9f2c7b1e is a shortened content hash: the full value is 64 hexadecimal characters after the algorithm. It is computed from the bytes, so it cannot change without a new digest. The full reference puts the tag before an @, the digest after.

### Why the last part wins

When a reference carries both a tag and a digest, the digest is what gets pulled. cosign signs the digest, not the tag, so verification is only meaningful against the digest. A tag that resolves to a different digest is a supply-chain event, even if it looks unchanged.

> **The honest caveat:** a digest proves the bytes are the bytes someone signed, not that those bytes are safe. Scanning still has to happen before the signature means anything.

> **The lesson:** deploy the digest, and let the tag be a comment for humans.

## In one line

> **The tag is a rumour.** The digest is the fact. Deploy the digest.

**Resolve the tag:** crane digest ghcr.io/acme/api:1.4.2
