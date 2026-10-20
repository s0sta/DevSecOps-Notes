---
id: p314
title: "The LLM API cheat sheet"
slug: the-llm-api-cheat-sheet
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [LLM, API, GenAI, CheatSheet, AIEngineering]
source: "LinkedIn post P314 · Visual series"
linkedin_date: 2028-09-28
design: cheatsheet
---

# The LLM API cheat sheet

The OpenAI-compatible request shape is now the common one, so the useful cheat sheet is not per vendor. It is one endpoint and the four checks around it.

## Quick reference

### Chat

```bash
curl -s $BASE/v1/chat/completions ...
curl -s $BASE/v1/models | jq '.data[].id'
jq -r '.choices[0].message.content'
jq -r '.choices[0].finish_reason'
export BASE=https://api.example.com
```

### Tokens

```bash
jq '.usage.prompt_tokens'
jq '.usage.completion_tokens'
jq '.usage.total_tokens'
wc -c prompt.txt  # ~4 chars per token
```

### Tools

```bash
jq '.tools[].function.name' req.json
jq '.choices[0].message.tool_calls'
jq '.choices[0].message.tool_calls[0]'
jq -r '.choices[0].finish_reason'
```

### Evals

```bash
python3 -m pytest evals -q
jq -r .score out/*.json | sort -n
jq '[.[] | select(.pass)] | length'
git diff --stat evals/baseline.json
```

## Explained

### Chat

The call is a POST to `$BASE`/v1/chat/completions with a model and a messages array. `curl -s` proves the endpoint answers, and a GET to `$BASE`/v1/models lists what you can call. Read choices[0].message.content for the answer and finish_reason for why it stopped: stop, length or tool_calls.

### Tokens

Every response carries a usage object. `jq '.usage.prompt_tokens'` and .completion_tokens give the two numbers that bill differently, and total_tokens is their sum. For a rough pre-flight estimate, run `wc -c` on the prompt and divide by four.

### Tools

You describe tools in the request as JSON schemas, each with a name and parameters. The model does not call them; it returns tool_calls with a name and an arguments string. Parse it, validate it against the schema, run your function, and send the result back as a tool message.

### Evals

Keep a folder of cases with expected answers and a score per case. Run them on every prompt change with `python3 -m pytest evals -q`, diff the scores against the baseline in git, and count the passes rather than reading a few outputs. An eval that is not in CI is an opinion.

> **The honest caveat:** compatible endpoints agree on the shape, not on the details. Tool-call formats, streaming chunks and token counts still differ between providers.

> **The lesson:** learn the shape once, then measure tokens and evals on every call.

## In one line

> **The API is small. The bill is not.** One endpoint, four checks, and a bill that grows quietly.

**Save the shape**

```bash
curl -s $BASE/v1/models
```
