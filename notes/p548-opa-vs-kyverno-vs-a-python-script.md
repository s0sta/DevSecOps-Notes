---
id: p548
title: "OPA vs Kyverno vs a Python script"
slug: opa-vs-kyverno-vs-a-python-script
sections: [devsecops]
topic: "Kubernetes"
tags: [OPA, Kyverno, Kubernetes, PolicyAsCode, DevSecOps]
source: "LinkedIn post P548 · PythonSec series"
linkedin_date: 2030-03-28
design: matrix
---

# OPA vs Kyverno vs a Python script

Three engineers describe policy as code and mean three different things: a Rego rule, a Kyverno YAML and a Python script in a cron job. They are not interchangeable; where the decision runs differs.

## Quick reference

| | **OPA** | **Kyverno** | **Python script** |
|:--|:--|:--|:--|
| Language | Rego | YAML and JMESPath | Python |
| Where it runs | Sidecar, CLI, library | In-cluster webhook | CI, cron, laptop |
| Admission | Only with Gatekeeper | Native | No, you build it |
| Ecosystem | Broad, CNCF | Kubernetes only | Cloud SDKs and APIs |
| Learning curve | Steep: Rego | Low: YAML | Low, but you own it |
| Best for | Cross-system policy | Kubernetes guardrails | Bespoke audits, diffs |

**How to pick**

- **OPA** → policy across Kubernetes, Terraform and CI.
- **Kyverno** → Kubernetes admission in YAML.
- **Python** → a diff, a report or a one-off audit.

## Explained

### Language and place

OPA speaks Rego, a general-purpose policy language, and runs as a sidecar, a CLI or a library. Kyverno speaks YAML with JMESPath and runs as an in-cluster webhook. Python runs wherever you start it: CI, cron or a laptop.

### Admission and ecosystem

OPA reaches admission through an admission controller such as Gatekeeper. Kyverno is native: it sees create and update, and can validate, mutate, generate and verify images. A Python script is not an admission controller; it audits a snapshot after the fact. OPA's ecosystem is broader: Kubernetes, Terraform, CI and Envoy. Kyverno is Kubernetes-only. Python has cloud SDKs and every API that prints JSON.

### Learning curve and fit

Rego is a new language, and it is not YAML. Kyverno is YAML most Kubernetes engineers know, with JMESPath for the tricky parts. Python is easiest to start and hardest to own: tests, retries and reports are yours. OPA suits policy that spans systems. Kyverno suits a Kubernetes-only platform that wants YAML and mutation. Python suits a bespoke cross-cloud audit, a diff or a report that no engine ships.

> **The honest caveat:** every one of them enforces only the rules someone wrote. Kyverno will happily mutate with a bad rule, and OPA will return deny for the wrong object.

> **The lesson:** pick the engine by where the decision has to be made.

## In one line

> **Where the decision has to be made.** The engine follows the enforcement point, not the fashion.

**Start with tests**

```bash
opa test policy/ -v
```
