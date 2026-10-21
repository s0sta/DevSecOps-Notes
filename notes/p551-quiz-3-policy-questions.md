---
id: p551
title: "Quiz: 3 policy questions"
slug: quiz-3-policy-questions
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [PolicyAsCode, OPA, Kyverno, DevSecOps, Kubernetes]
source: "LinkedIn post P551 · PythonSec series"
linkedin_date: 2030-04-04
design: quiz
---

# Quiz: 3 policy questions

A policy quiz is easy until the policy is the thing standing between a typo and a production cluster. Three questions from this phase.

## Quick reference

**Q1. Why does a policy need a test before it enforces anything?**

- a) So it returns deny for a known bad fixture
- b) So the YAML parses in the editor
- c) So the policy is longer than the app

> **Answer:** a) So it returns deny for a known bad fixture. A policy is code: a typo in a selector can allow everything. A test pins the decision for a known object before a cluster or a pipeline relies on it.

**Q2. Why run a policy in audit mode before enforce?**

- a) To see what would fail without blocking it
- b) To make the policy run faster
- c) To skip the admission webhook

> **Answer:** a) To see what would fail without blocking it. Audit records would-be violations on real traffic, so you find broken workloads and false positives before a deny stops a deploy.

**Q3. Why is a Python script not an admission controller?**

- a) It runs on a schedule, not in the request path
- b) It cannot read JSON
- c) It cannot return an exit code

> **Answer:** a) It runs on a schedule, not in the request path. Admission needs a webhook in the API server path with TLS, latency and high availability. A script audits a snapshot; it cannot block a create.

## Explained

### Question one

Why does a policy need a test? Because a policy is code, and a selector typo can allow everything. A test pins the decision for a known object: this pod must be denied, this one must be allowed. opa test or kyverno test runs those fixtures before a cluster or a pipeline relies on the rule. A test that only checks the happy path is a demo.

### Question two

Why run in audit mode before enforce? Audit records what would have been denied on real traffic without blocking it. You find the workloads that would break and the rules that would block too much, fix them, then switch to enforce. A deny that arrives with the first deploy is an outage.

### Question three

Why is a Python script not an admission controller? Admission is a webhook in the API server request path, with TLS, a latency budget and high availability. A script audits a snapshot on a schedule. It can tell you what is wrong; it cannot stop the create that is wrong now.

> **The honest caveat:** passing this quiz does not enforce anything. The test, the audit run and the webhook do.

> **The lesson:** test the rule, audit the rollout, then let admission enforce.

## In one line

> **Test, audit, then enforce.** Three answers that keep policy out of production surprises.

**Test a rule**

```bash
opa test policy/ -v
```
