---
id: p163
title: "Anatomy of a container image reference"
slug: anatomy-of-a-container-image-reference
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, Containers, DevOps, CloudNative, Security]
source: "LinkedIn post P163 · IT series"
linkedin_date: 2027-10-12
design: anatomy
---

# Anatomy of a container image reference

A container image name looks simple, but each part answers a different question, and the last part is the one that guarantees you run exactly what you think you run.

## Quick reference

```text
registry.io/team/api:1.4.2@sha256:9f3c
```

| Part | Name | What it means |
|:--|:--|:--|
| `registry.io` | Registry | Where the image lives. Defaults to Docker Hub if omitted. |
| `/team` | Namespace | The owner or organisation on that registry. |
| `/api` | Repository | The image's name within that namespace. |
| `:1.4.2` | Tag | A human label for a version. It can be moved. |
| `@sha256:9f3c` | Digest | The exact content hash. Immutable. This is the real identity. |

## Explained

`registry.io` is the registry: where the image is stored. Leave it off and the tool defaults to Docker Hub, which is why docker pull nginx quietly reaches out to a public registry. In production you usually name a private or cloud registry explicitly.

`/team` is the namespace: the user or organisation that owns the image on that registry. It keeps names from colliding between teams and projects.

`/api` is the repository: the image's own name within that namespace. Registry, namespace and repository together point at a place.

:1.4.2 is the tag: a human-friendly label for a version. The catch is that a tag is just a pointer and can be moved. Someone can push a new image to :1.4.2, or to latest, and the name now points somewhere different. Same name, different bytes.

@sha256:9f3c... is the digest: a cryptographic hash of the exact image content. It never changes, because changing the content changes the hash. This is the image's true identity.

Why it matters: a tag answers "roughly which version?", a digest answers "exactly which bytes?". For reproducible, tamper-evident deploys, pin the digest. Many teams tag for humans and deploy by digest, getting both readability and certainty.

## In one line

> **Pin the digest for certainty.** Tags are convenient. Digests are exact.

**See the digest**

```bash
docker image inspect api:1.4.2 --format '{{.Id}}'
```
