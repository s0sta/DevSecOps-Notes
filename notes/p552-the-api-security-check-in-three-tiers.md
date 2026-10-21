---
id: p552
title: "The API security check, in three tiers"
slug: the-api-security-check-in-three-tiers
sections: [devsecops]
topic: "Application & API security"
tags: [API, OpenAPI, DevSecOps, Python, CyberSecurity]
source: "LinkedIn post P552 · PythonSec series"
linkedin_date: 2030-04-07
design: architecture
---

# The API security check, in three tiers

The API review starts with a list of endpoints somebody typed from memory. The OpenAPI file says one thing, the gateway route table says another, and the endpoint nobody listed is the one that never got reviewed.

## Quick reference

- **Spec:** OpenAPI file (SPEC) · Gateway routes (ROUTE)
- **Checks:** Auth per operation (AUTH) · Input shape (INPUT) · Header rules (HDR)
- **Report:** Findings list (FIND) · Exit gate (GATE)

**Request flow:** OpenAPI file → Auth per operation → Findings list → Exit gate; OpenAPI file → Input shape → Findings list; Gateway routes → Header rules → Findings list

**Around it:** CI job (CI)

## Explained

### Spec

The first tier is the spec: the OpenAPI file and the gateway route table. Diffing the two finds the shadow endpoint, live in the gateway and absent from the spec, which means absent from every review that trusted the spec.

### Checks

The second tier runs three checks per operation. Auth asks whether the operation declares a security requirement, inherited from the root or set on the operation. Input shape asks whether the body and parameters have a schema with types, lengths and enums. Header rules ask whether the response carries the security headers the platform promises. Every finding keeps its method and path.

### Report

The third tier is the findings list and the exit gate, read by the CI job. Exit 1 means at least one check failed, exit 0 means clean, exit 2 means the spec will not parse. That exit code is the point: a report nobody gates on is a PDF.

> **The honest caveat:** a green gate proves the spec declares these controls, not that the running service enforces them. Compare the spec with live responses before you trust the badge.

> **The lesson:** audit the spec, then prove the service matches it.

## In one line

> **Spec, check, gate. Nothing skips a tier.** A finding you cannot trace to a check is a finding nobody fixes.

**Check the spec**

```bash
python3 openapi_auth_check.py api.json
```
