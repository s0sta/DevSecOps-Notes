---
id: p318
title: "Tokens, context and cost, drawn"
slug: tokens-context-and-cost-drawn
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [LLM, Tokens, GenAI, AIEngineering, FinOps]
source: "LinkedIn post P318 · Visual series"
linkedin_date: 2028-10-08
design: explainer
---

# Tokens, context and cost, drawn

You paste a forty-page PDF into a prompt and the bill lands well above the estimate. Nothing was wrong with the model; the four numbers behind the price were never measured.

## Quick reference

### Tokens

- Text becomes tokens before the model sees it
- English prose runs at about four chars per token
- Code, JSON and other languages cost more
- The tokeniser is part of the contract

### Context window

- One budget shared by prompt and answer
- History, retrieved text and output all count
- Past the limit: truncated or rejected
- Every turn re-sends the history

### Input vs output

- Both billed per million tokens
- Output is the more expensive direction
- Input is one parallel pass; output is a loop
- A long answer is the cost you control least

### Caching

- A hit skips the repeated prompt prefix
- Providers bill the hit at a lower input rate
- It rewards a stable prefix
- Put the variable part last

> **Note:** The context window is a budget, and the bill is per token.

## Explained

### Tokens

Text is cut into tokens before the model sees it: words, parts of words, punctuation. English prose runs at roughly four characters per token, so a thousand words is about fifteen hundred tokens. Code, JSON and other languages cost more, because their patterns are less predictable.

### The context window

The window is one budget shared by the prompt, the conversation so far, retrieved text and the answer. Past the limit, content is truncated or the request is rejected outright. Every turn re-sends the history, which is why a long chat grows more expensive.

### Input versus output

Both directions are billed per million tokens, at different prices, and output is the more expensive one. Output is generated one token at a time, each step reading the weights, while input is processed in one parallel pass. A long answer is the cost you control least once it starts.

### Caching

A cache hit skips the recomputation of a prompt prefix you have sent before, and providers bill that prefix at a lower input rate. It rewards a stable prefix: instructions and reference document first, the variable question last.

> **The honest caveat:** token counts differ by tokeniser, and cache rules differ by provider, so the number that settles an argument is your own usage report.

> **The lesson:** measure tokens, context and cache hits before you argue about the model.

## In one line

> **Every token is on the bill.** Context is a budget; output is the expensive half.

**Measure a prompt**

```bash
jq .usage resp.json
```
