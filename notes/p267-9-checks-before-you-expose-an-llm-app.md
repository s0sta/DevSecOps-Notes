---
id: p267
title: "9 checks before you expose an LLM app"
slug: 9-checks-before-you-expose-an-llm-app
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [LLM, AISecurity, DevSecOps, CloudNative, CyberSecurity]
source: "LinkedIn post P267 · Platform series"
linkedin_date: 2028-06-11
design: checklist
---

# 9 checks before you expose an LLM app

An LLM feature is an endpoint that takes free text and can call tools. That is a wider attack surface than most, and the checks that make it safe are boring.

## Quick reference

### Input

- **Test injections in CI** — prompt plus poisoned doc
- **Rate limit per tenant** — requests and tokens
- **Redact PII on the way in** — email, card, phone

### Tools

- **Scope every tool call** — verbs, not admin
- **Approve state changes** — human in the loop
- **Keep one kill switch** — tested, not assumed

### Output

- **Validate every output** — schema and allow-list
- **Log with a trace ID** — redacted prompt
- **Eval before you ship** — a fixed test set

## Explained

### Input

Test injections in CI. Keep a set of prompts and poisoned documents that try to override your instructions, and run them on every prompt change. If one succeeds, the build fails.  
Rate limit per tenant. Requests and tokens both. Without it, one user with a loop can spend your whole budget and starve everyone else.  
Redact PII before the model sees it. Email, card and phone patterns are cheap to catch, and a prompt that never carried the data cannot leak it.

### Tools

Scope every tool. The model should call a function with the verbs it needs, not hold a credential. A read-only search tool cannot delete a table, however the prompt is written.  
Approve what changes state. Payments, emails, deletions and deploys get a human confirmation. Read-only actions can run unattended.  
Keep one flag that stops the agent. A kill switch that drops tool calls and returns a safe message, tested.

### Output

Validate output against a schema and an allow-list. Never pass model output straight into SQL, a shell or the DOM.  
Log with a trace ID: redacted prompt, response, model version, latency, token counts.  
Evaluate before you ship. A fixed test set rerun on every model or prompt change.

> **The honest caveat:** a checklist is not a control until someone runs it.

> **The lesson:** the checks are not about the model. They are about everything around it.

## In one line

> **Expose the app, not the model.** Nine checks that keep an LLM feature inside its lane.

**First check:** add one injection test to CI
