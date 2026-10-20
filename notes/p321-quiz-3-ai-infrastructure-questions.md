---
id: p321
title: "Quiz: 3 AI infrastructure questions"
slug: quiz-3-ai-infrastructure-questions
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [AIInfrastructure, GPU, LLM, GenAI, SystemDesign]
source: "LinkedIn post P321 · Visual series"
linkedin_date: 2028-10-15
design: quiz
---

# Quiz: 3 AI infrastructure questions

The last post of this 50-part series, and the right place to stop: the layer that decides what the AI systems of this path actually cost. Three questions. Answer before the reveal.

## Quick reference

**Q1. A GPU shows 100 percent utilisation but few tokens per second. Why?**

- a) Decode is bound by memory bandwidth
- b) The card has too few CUDA cores
- c) The model is too small to fill the card

> **Answer:** a) Decode is bound by memory bandwidth. Each generated token reads the weights once, so bytes moved, not maths, set the pace. Batching spreads that read, and HBM bandwidth is the number to compare.

**Q2. What does TTFT measure?**

- a) Time from request to the first token
- b) Time to finish the whole answer
- c) Time the request waits in the queue

> **Answer:** a) Time from request to the first token. Queueing plus prefill, the pass over your prompt. It grows with prompt length and with the number of requests ahead, and it is the latency the user feels first.

**Q3. Why do output tokens cost more than input tokens?**

- a) Decode generates one token per step
- b) Output is stored for longer
- c) Output tokens are larger

> **Answer:** a) Decode generates one token per step. Prefill processes the prompt in parallel; decode generates a token per step and reads the weights each step, so a generated token costs more than a read one.

## Explained

### Question one

A GPU reports 100 percent utilisation but few tokens per second. Why? Decode is bound by memory bandwidth, not by maths. Each generated token reads the weights once, so the bytes moved set the pace; batch more requests and the same weights serve more tokens.

### Question two

What does TTFT measure? The time from request to the first token, which is queueing plus prefill. Prefill processes the whole prompt in one pass, so a long prompt and a busy queue both push the number up, and the user feels every millisecond of it.

### Question three

Why do output tokens cost more than input tokens? Because prefill handles the prompt in parallel, while decode generates one token per step and re-reads the weights each time. A generated token takes more GPU time than a read one, and the price follows the time.

> **The honest caveat:** passing this quiz does not make a cluster efficient; the measurements do.

If you got these, you are reading the system, not the demo. That is the discipline.

That is the series. Fifty posts, from a cable to a GPU cluster, drawn one page at a time, plus ten Python scripts you can run today. Thank you for following along.

## In one line

> **Draw the whole system.** Fifty posts, one idea: measure the system, not the demo.

**Keep measuring**

```bash
nvidia-smi dmon -s mu -d 5
```
