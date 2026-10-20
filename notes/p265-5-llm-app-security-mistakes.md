---
id: p265
title: "5 LLM app security mistakes"
slug: 5-llm-app-security-mistakes
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [LLMSecurity, GenAI, CyberSecurity, AppSec, DevSecOps]
source: "LinkedIn post P265 · Platform series"
linkedin_date: 2028-06-06
design: dontdo
---

# 5 LLM app security mistakes

The model is not a security boundary. It runs on text, it cannot tell an instruction from data, and it will follow the last convincing sentence in its context. These five mistakes all come from forgetting that.

## Quick reference

**1.** ❌ **The model holds permissions** — A prompt can spend any credential the model was given.  
✅ **A tool with a narrow scope** — Your code calls the tool. The model never sees the credential.

**2.** ❌ **Secrets in the system prompt** — The prompt is logged, echoed and extractable.  
✅ **Keys in the runtime only** — The model gets a placeholder, never the key itself.

**3.** ❌ **Unbounded agency** — A shell, a browser and write access, driven by text.  
✅ **Small tool set, human approval** — State changes wait for a person. Reads can run alone.

**4.** ❌ **Rendering output as HTML** — An answer becomes script in your page: stored XSS.  
✅ **Render as text or sanitise** — Model output is untrusted input to the DOM.

**5.** ❌ **Logging raw prompts** — PII and keys get copied to weaker storage for months.  
✅ **Redact on write** — Store a hash or a redacted copy, not the raw text.

## Explained

### Permissions

Trusting the model with permissions. Give the model a database credential or an admin token and a prompt can spend it. The fix is a tool with a narrow scope, called by your code, not a credential handed to the model.

### Secrets and agency

Secrets in the system prompt. The system prompt is not private: it is logged, echoed back, and extractable with the right question. Keep keys in the runtime and out of every prompt.

Unbounded agency. A model with a shell, a browser and write access can be talked into using them. Limit the tools to the smallest set, and require approval for anything that changes state.

### Output and logs

Rendering output as HTML. Model output is untrusted input. Render it as text or sanitise it, or an answer becomes stored XSS.

Logging raw prompts. Prompts carry PII, keys and customer data, and logs get copied to cheaper storage with weaker access. Redact on write.

> **The honest caveat:** a better prompt is not a fix for any of these. It is a mitigation that fails open when the model is persuaded.

The habit that matters: every time you are tempted to fix one of these with a prompt, ask whether a permission or a validator would hold when the prompt fails.

## In one line

> **A prompt is advice. A permission is a limit.** Every fix moves a decision out of the prompt.

**Scope the tool:** one tool, one verb, no admin
