---
id: p313
title: "Anatomy of an agent, drawn"
slug: anatomy-of-an-agent-drawn
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [AIAgents, LLM, GenAI, AIEngineering, SystemDesign]
source: "LinkedIn post P313 · Visual series"
linkedin_date: 2028-09-26
design: explainer
---

# Anatomy of an agent, drawn

A chat model answers. An agent acts, and the difference is four parts bolted around the same model. Take one away and it fails in a way you can predict.

## Quick reference

### Planner - the loop

- Turns one goal into ordered steps
- Picks the next call, reads the result
- Stops on success, error or budget
- The loop is the product, not the prompt

### Tools - typed calls

- A tool is a function with a schema
- The model proposes the arguments
- Your code validates and runs them
- Results are untrusted input

### Memory - two speeds

- Short-term: the messages in this run
- Long-term: a store it can search
- Both grow until something breaks
- Write less than you read, then expire

### Guardrails - the limits

- Allow-list the tools, scope the token
- Validate arguments before the call
- Cap steps, spend and wall-clock time
- The only part you can test with certainty

> **Note:** A model with tools and no guardrail is a remote shell with a chat interface.

## Explained

### The planner

The planner turns a goal into steps, picks the next tool call, reads the result and decides again. That loop needs a stopping rule: success, an error it cannot recover from, or a budget cap. Without the cap, a confused agent keeps buying tokens.

### The tools

A tool is a function with a typed schema: a name, arguments, and what it returns. The model proposes the arguments; your code validates them and makes the call. That split is the point, because the model never executes anything itself.

### The memory

Short-term memory is the message list of the current run, and it grows until it meets the context window. Long-term memory is a store the agent can search, written deliberately and read rarely. Both need a rule for what to forget.

### The guardrails

Guardrails live outside the model: an allow-list of tools, a scoped token per tool, schema validation on every argument, and caps on steps, spend and wall-clock time. They are the part you can test with certainty.

> **The honest caveat:** a better planner does not fix a tool with too much permission, and a guardrail cannot make a bad plan good.

> **The lesson:** build the loop, then build the limits around it.

## In one line

> **An agent is a loop with limits.** The plan is probabilistic; the limits around it are not.

**Watch one run:** log every tool call and its result
