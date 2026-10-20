---
id: p266
title: "A prompt's journey through a gateway"
slug: a-prompts-journey-through-a-gateway
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [LLM, GenAI, AIEngineering, DevOps, SRE]
source: "LinkedIn post P266 · Platform series"
linkedin_date: 2028-06-08
design: timeline
---

# A prompt's journey through a gateway

A prompt leaves your app and reaches a model in under a second. Between those two points a gateway can do six things, and every one of them is a place to fail safely.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **1** | The request arrives | App sends prompt, tenant and trace IDs; the gateway normalises. |
| **2** | Auth and quota | The key resolves to a tenant, then rates and quotas are checked. |
| **3** | The guardrail runs | Input filters catch PII, blocked topics and injection patterns. |
| **4** | Retrieval | Top-k chunks from the tenant index, as data, not instructions. |
| **5** | The model call | Provider call with a timeout, a retry budget and a fallback model. |
| **6** | Check and log | Schema check, secret scan, redaction, then one trace-ID log line. |

## Explained

### Before the model

1. **The request arrives.** Your app sends the prompt, a tenant ID and a trace ID. The gateway normalises the call so every provider looks the same.

2. **Auth and quota.** The key resolves to a tenant, then a rate limit checks requests per minute and tokens per minute. Over quota returns 429, not a queue that grows all night.

3. **The guardrail runs.** Input filters check for PII, blocked topics and injection patterns. A hit is logged and returned as a policy refusal, before a token is spent.

### At the model

4. **Retrieval.** The gateway embeds the question, fetches the top-k chunks from the tenant's index, and inserts them as data, not instructions.

5. **The model call.** The prompt goes to the provider with a timeout, a retry budget and a fallback model. Streaming starts as soon as the first token arrives.

### After the model

6. **Check and log.** The response is validated against a schema, scanned for secrets, redacted, then logged with the trace ID. Only then does your app see it.

> **The honest caveat:** each hop costs milliseconds, and a gateway that checks everything becomes the reason your app feels slow.

> **The lesson:** a gateway is not a proxy. It is the one place where every prompt and every answer can be inspected in a single code path.

## In one line

> **Every hop is a control.** A gateway is where a prompt becomes auditable.

**Trace one prompt**

```bash
grep trace_id gateway.jsonl
```
