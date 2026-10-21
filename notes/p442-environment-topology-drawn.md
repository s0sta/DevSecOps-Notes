---
id: p442
title: "Environment topology, drawn"
slug: environment-topology-drawn
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, Environments, CICD, CloudNative, SRE]
source: "LinkedIn post P442 · DevOps series"
linkedin_date: 2029-07-24
design: architecture
---

# Environment topology, drawn

A pull request opens and ninety seconds later a URL answers with the change running. That is the first tier of an environment topology, and it is the one most teams never build.

## Quick reference

- **Dev · Ephemeral:** Pull request (PR) · Preview environment (ENV) · Preview URL (URL)
- **Staging · Shared:** Shared staging (STG) · Seeded data (SEED) · Smoke tests (SMOKE)
- **Prod · Multi-az:** Load balancer (LB) · App, multi-AZ (APP) · Read replica (READ)

**Request flow:** Pull request → Preview environment → Preview URL; Preview environment → Shared staging → Smoke tests → Load balancer → App, multi-AZ → Read replica; Seeded data → Shared staging

## Explained

### Three tiers

DEV is ephemeral. Each pull request gets its own namespace, its own deployment and its own preview URL, built from the same chart as production. Close or merge the request and the namespace goes with it, which is what keeps the tier cheap and honest.

STAGING is shared. One deployment per team, one known dataset loaded from fixtures, and a smoke test that runs after every deploy. Staging exists to catch integration, not to be a second production.

PROD is multi-AZ. A load balancer spreads traffic across zones, the application runs in more than one, and a read replica takes the reporting queries. It differs by scale and topology, not by build.

### One path

The same artefact is promoted: the image digest that passed the preview is the digest that reaches staging and production. Only the configuration differs between tiers, which is factor three of the twelve-factor app. The seeded staging data is synthetic, never a copy of customer records.

> **The honest caveat:** a preview environment is only a preview if it runs the same services and versions. Add a different database engine or skip a queue and you are testing a demo.

> **The lesson:** the three tiers are one system at different sizes, and the promotion path is the product.

## In one line

> **Same code, different config.** Promote the artefact, never rebuild it for the next tier.

**Check the digest**

```bash
docker image inspect api:1.4.2
```
