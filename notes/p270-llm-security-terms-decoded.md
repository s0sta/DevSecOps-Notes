---
id: p270
title: "LLM security terms, decoded"
slug: llm-security-terms-decoded
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [LLMSecurity, AISecurity, GenAI, CyberSecurity, CloudNative]
source: "LinkedIn post P270 · Platform series"
linkedin_date: 2028-06-18
design: reveal
---

# LLM security terms, decoded

A model that only talks is a small risk. The moment it reads your documents and calls your tools, it is a system, and systems fail in named ways. Six terms cover most of it.

## Quick reference

- **prompt injection** — Text in the input tells the model to ignore its instructions. Indirect injection arrives through a document, a page or a tool result.
- **jailbreak** — A prompt that gets around the model's safety training: role-play, encoding, or a long story that walks it past a refusal.
- **RAG poisoning** — Planting content in the corpus the retriever will surface, so the model answers with it or follows it as instruction.
- **data leakage** — The model revealing what it should not: another tenant's context, a secret in the system prompt, or PII in a log.
- **excessive agency** — Giving the model tools and permissions beyond the task, so a bad prompt can act, not just answer.
- **guardrail** — A check outside the model: input filters, schema validation, allow-lists and human approval, enforced in code.

## Explained

### The attacks

Prompt injection is the core problem. Text in the input tells the model to ignore its instructions. Direct injection comes from the user; indirect injection arrives inside a retrieved document, a web page or a tool result, which is why RAG turns every document into an attack surface.

A jailbreak gets around the model's safety training: role-play, encoding, a story that walks past a refusal. It targets the model's policy, not your application's instructions.

RAG poisoning is planting content in the corpus the retriever will surface, so the model answers with it, or follows it as instruction.

### The exposure

Data leakage is the model revealing what it should not: another tenant's context, a secret in the system prompt, or PII in a log.

Excessive agency is giving the model tools and permissions beyond the task, so a bad prompt can act, not just answer.

### The control

A guardrail is any check outside the model: input filters, schema validation, allow-lists, human approval. The model proposes; the guardrail decides.

> **The honest caveat:** none of these terms is a control on its own. An input filter misses an injection that arrives by retrieval, and a jailbreak is not an attack on your app until a tool acts on it.

> **The lesson:** name the failure mode before you pick the control, because the control lives outside the model.

## In one line

> **Name it, then control it.** A named failure mode is halfway to a control.

**Start here:** treat retrieved text as data
