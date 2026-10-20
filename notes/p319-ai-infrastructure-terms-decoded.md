---
id: p319
title: "AI infrastructure terms, decoded"
slug: ai-infrastructure-terms-decoded
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [AIInfrastructure, GPU, LLM, Inference, MachineLearning]
source: "LinkedIn post P319 · Visual series"
linkedin_date: 2028-10-10
design: reveal
---

# AI infrastructure terms, decoded

The dashboard says the GPU is busy and users still complain. Utilisation is not latency, and these six words are how you tell the difference.

## Quick reference

- **TTFT** — Time to first token: how long the user stares at nothing before the answer starts. It covers the queue and the prefill pass.
- **tokens/s** — Decode throughput: how fast tokens arrive after the first one. Batching raises the total while a single request slows down.
- **batching** — Packing several requests into one forward pass. Static batching waits for a full batch; continuous swaps requests every step.
- **KV cache** — The attention keys and values kept from earlier tokens so they are not recomputed. It buys speed and costs memory, one per request.
- **quantisation** — Weights stored in fewer bits: FP16 down to INT8 or FP8. Less memory, faster maths, and an accuracy loss to measure.
- **MIG** — Multi-Instance GPU: one card split into isolated slices, each with its own memory and compute. For sharing, not for one big job.

## Explained

### TTFT

Time to first token is how long the user stares at nothing before the answer starts. It covers the queue plus prefill, the pass over the prompt, so it grows with prompt length.

tokens/s

Decode throughput is how fast tokens arrive after the first one. It is measured per request or across the batch, and the two move in opposite directions: more requests raise the total while one request slows down.

### Batching

Packing several requests into one forward pass. Static batching waits for a full batch; continuous batching adds and removes requests at every step, which is why serving engines hold a queue.

### KV cache

The attention keys and values kept from earlier tokens so they are not recomputed. It buys speed and costs memory, one cache per concurrent request, which is the real ceiling on users per card.

### Quantisation

Storing weights in fewer bits, from FP16 down to INT8 or FP8. Less memory and faster matrix maths, at the risk of a small accuracy loss you measure rather than assume.

### MIG

Multi-Instance GPU splits one card into isolated slices, each with its own memory and compute. Good for sharing a card, not for making one large job fit.

> **The honest caveat:** every term is a trade, none is a target. A high tokens per second figure on an idle cluster is worth nothing.

> **The lesson:** name the number before you tune anything.

## In one line

> **Name the number before you tune.** Each term is a lever, and every lever has a cost.

**Watch one card**

```bash
nvidia-smi dmon -s mu -d 2
```
