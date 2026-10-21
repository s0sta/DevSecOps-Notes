---
id: p542
title: "Policy as code, in three tiers"
slug: policy-as-code-in-three-tiers
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [PolicyAsCode, OPA, DevSecOps, Kubernetes, CloudNative]
source: "LinkedIn post P542 · PythonSec series"
linkedin_date: 2030-03-14
design: architecture
---

# Policy as code, in three tiers

A team writes its first Rego rule, runs it once in a terminal, and calls it policy as code. Six weeks later the rule is not in CI, the cluster carries a different version, and nobody can say which one is live.

## Quick reference

- **Source:** Policy files (REGO) · Policy tests (TEST)
- **Evaluate:** OPA engine (OPA) · CI step (CI)
- **Enforce:** Admission (ADMIT) · Report (OUT)

**Request flow:** Policy files → OPA engine → CI step → Admission → Report; Policy tests → OPA engine

## Explained

### The three tiers

Source. Two nodes: policy files and policy tests. The files are Rego; the tests are fixtures with expected allow and deny decisions. Both sit in the same repository and go through the same review as the application.

Evaluate. The policy files and the tests feed the OPA engine. Its decision goes to a CI step, which runs the tests and evaluates the manifests in the pull request. A rule that fails its own tests never reaches a cluster.

Enforce. The same bundle reaches admission, which sees every create and update, and a report, which records what was allowed and denied. The arrows run from files and tests into the engine, from the engine into CI, then from CI to admission, and from admission to the report. Admission is the gate; the report is the evidence, and without it the gate is a decision nobody can audit later.

### The drift

The gap between source and enforce is where drift lives: a hotfix at admission, a deleted test, a bundle never rebuilt.

> **The honest caveat:** an engine only enforces the rules someone wrote and tested. A selector typo can pass every test written for the wrong object.

> **The lesson:** write the rule, test the decision, then enforce the same bundle in both places.

## In one line

> **Source, evaluate, then enforce.** A policy that is not tested is a wish with YAML around it.

**Test one rule**

```bash
opa test policy/ -v
```
