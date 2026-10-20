---
id: p262
title: "The LLM application stack, layer by layer"
slug: the-llm-application-stack-layer-by-layer
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [AI, LLM, DevSecOps, MLOps, CloudNative]
source: "LinkedIn post P262 · Platform series"
linkedin_date: 2028-05-30
design: stack
---

# The LLM application stack, layer by layer

An LLM feature that works in a demo is a model call. One that works in production is a stack of six layers, and the model is only the bottom one.

## Quick reference

*Bottom to top: each layer changes the answer*

1. **Model** — The foundation model: a hosted API, open weights or a fine-tune. · *model*
2. **Gateway** — One endpoint in front: keys, quotas, retries, routing and logs. · *gateway*
3. **Retrieval** — Chunks, embeddings and a vector index, so answers use your data. · *retrieval*
4. **Orchestration** — The loop that plans, calls tools and assembles the final prompt. · *agent loop*
5. **Guardrails** — Input and output checks: PII, injection, schema and policy. · *guardrails*
6. **Evals** — Scored test sets that gate a prompt or model change before release. · *evals*

## Explained

### The lower layers

Model. A hosted API, an open-weight model or a fine-tune. The choice sets cost, latency, context window and what data leaves your network.

Gateway. One endpoint in front of every model: keys, quotas, retries, routing and logs. Without it, every team hard-codes a different provider key.

Retrieval. Chunks, embeddings and a vector index, so the model answers from your documents instead of its training data. The quality of the chunks matters more than the model choice.

### The upper layers

Orchestration. The loop that plans, calls tools and assembles the prompt. It is where an agent lives, and where most latency and most failure modes live too.

Guardrails. Input and output checks: PII, prompt injection, schema validation, policy. They sit around the model, not inside it.

Evals. Scored test sets that gate a prompt or model change before release. Without them, every change is a vibe check. Start with thirty real questions and a pass mark.

> **The honest caveat:** evals are the weakest layer in most teams. An LLM judge is useful, but it correlates with quality rather than proving it, so keep a small human-reviewed set.

> **The lesson:** debug the layer, not the model.

## In one line

> **The model is one layer.** Every layer above it can change the answer.

**Start with evals:** pick 30 real questions and score them
