---
id: p561
title: "Quiz: 3 web security questions"
slug: quiz-3-web-security-questions
sections: [devsecops]
topic: "Application & API security"
tags: [WebSecurity, API, DevSecOps, CyberSecurity, HTTP]
source: "LinkedIn post P561 · PythonSec series"
linkedin_date: 2030-04-28
design: quiz
---

# Quiz: 3 web security questions

Three questions from a web security review. The answers are short, and each one is a place where a control is trusted for more than it does.

## Quick reference

**Q1. Why is CSP not XSS-proof?**

- a) It only blocks inline script
- b) It restricts sources, not code
- c) Browsers ignore it now

> **Answer:** b) It restricts sources, not code. CSP limits where script can load from and whether inline code runs, not what an allowed script does. A JSONP host or a DOM sink in your own bundle still executes.

**Q2. Why is a wildcard with credentials a bug?**

- a) Browsers reject the pair
- b) Any origin could read the data
- c) It disables HTTPS

> **Answer:** b) Any origin could read the data. The pair would let any origin read authenticated responses, so browsers reject it. The usual fix, echoing the Origin, turns the rejection into a working bypass.

**Q3. Why can 404 be safer than 403?**

- a) It hides whether the object exists
- b) It skips authentication
- c) It is faster to render

> **Answer:** a) It hides whether the object exists. 403 confirms the object exists and the caller lacks permission. 404 gives the same answer for missing and forbidden ids, so enumeration gets slower.

## Explained

### Why CSP is not XSS-proof

It restricts where script comes from, not what a permitted script does. An allowlisted host can serve a JSONP endpoint, and a DOM sink inside your own bundle is still a sink. CSP raises the cost; it does not remove the class. That is why an XSS review still needs output encoding and a DOM audit.

### Why the wildcard plus credentials is a bug

The pair would let any origin read authenticated responses, so browsers reject it. The bug is the intent: the usual fix echoes the request origin back, and that turns a rejected header into a working bypass. The safe pattern is an exact allowlist checked on the server, with credentials only for those origins.

### Why 404 can be safer than 403

403 confirms the object exists and the caller lacks permission. 404 gives the same answer for a missing id and a forbidden one, so an attacker cannot enumerate another tenant's objects. It turns a permission bug into a missing-object bug, which is harder to debug.

> **The honest caveat:** CSP still earns its place, and returning 404 for everything can confuse legitimate users. Both are judgement calls, not defaults.

> **The lesson:** test the control, not the badge.

## In one line

> **The gap is in the assumption.** Three answers worth checking against your own stack.

**Re-read the policy**

```bash
curl -sI $URL
```
