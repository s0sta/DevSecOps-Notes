---
id: p422
title: "The release path, drawn"
slug: the-release-path-drawn
sections: [devsecops]
topic: "Release & build engineering"
tags: [DevOps, ReleaseEngineering, CICD, Kubernetes, SRE]
source: "LinkedIn post P422 · DevOps series"
linkedin_date: 2029-06-07
design: architecture
---

# The release path, drawn

A release often starts with a rebuild, and that is the first mistake. The pipeline that tested the image should not build another one for production; it should promote what it already signed.

## Quick reference

- **Artifact:** Signed image (IMG) · Release manifest (MAN)
- **Environment:** Staging (STG) · Pre-production (PRE)
- **Traffic:** Canary (CAN) · Stable (STB)

**Request flow:** Signed image → Release manifest → Staging → Pre-production → Canary → Stable

## Explained

### The artefact

The first tier is ARTIFACT: a signed image, with a digest that identifies the exact bytes, and a manifest that records the digest, the source commit and the build. Signing does not make the image safe; it proves who built it and that nobody swapped it afterwards.

### The environment

The second tier is ENVIRONMENT: staging, then pre-production. Both receive the same digest, never a fresh build. Staging answers "does it work"; pre-production answers "does it work with production-shaped configuration and data". A rebuild here would quietly invalidate every test that came before.

### The traffic

The third tier is TRAFFIC: a canary and a stable slice. The canary takes a small share, and you compare its error rate and latency against the stable version. Then it grows, or the traffic returns. The arrows run from the image to the manifest, into staging and pre-production, then to the canary and stable.

> **The honest caveat:** a signature proves provenance, not quality. A signed image can still carry a bad migration.

> **The lesson:** build once, sign once, then move the same digest down the path, and let each environment answer one question.

## In one line

> **Promote, do not rebuild.** One signed digest, every environment, no second build.

**Promote the digest**

```bash
kubectl set image deploy/api api=$IMAGE
```
