---
id: p268
title: "6 GPU numbers for platform teams"
slug: 6-gpu-numbers-for-platform-teams
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [GPU, NVIDIA, Kubernetes, H100, CloudNative]
source: "LinkedIn post P268 · Platform series"
linkedin_date: 2028-06-13
design: numbers
---

# 6 GPU numbers for platform teams

A GPU node is not a bigger CPU node. It has its own scheduling unit, memory ceiling and power budget, and these six numbers decide capacity.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **1** | GPU per request | H100 SXM: one `nvidia.com/gpu` request is a whole card. | k8s |
| **8** | GPUs per HGX board | H100 SXM: an HGX baseboard carries eight cards on NVLink. | hardware |
| **80 GB** | HBM3 per GPU | H100 SXM: the memory ceiling for one model shard. | memory |
| **3.35** | TB/s bandwidth | H100 SXM: HBM3 bandwidth, the limit for token speed. | hbm3 |
| **700 W** | Board power | H100 SXM: plan cooling for eight of these in one node. | power |
| **7** | MIG slices | H100 SXM: split one card into seven small instances. | sharing |

## Explained

### Scheduling

One GPU per request. Kubernetes schedules GPUs as whole devices. A container asks for `nvidia.com/gpu`: 1 and the device plugin hands it one card. There is no fractional request unless you configure sharing.

Eight per HGX board. An HGX H100 baseboard carries eight SXM GPUs joined by NVLink, which is why GPU nodes are sold in eights and why one node failure takes eight cards with it.

### Memory and bandwidth

80 GB of HBM3. That is the memory on one H100 SXM, and it sets the largest model shard you can fit before you need tensor parallelism across cards.

3.35 TB/s. The HBM3 bandwidth on the same card. Inference on a large model is memory-bound, so this number, not the FLOPs, often decides tokens per second.

### Power and sharing

700 W. The board power of an H100 SXM. Eight of them plus CPUs and fans is a multi-kilowatt node, and the rack and cooling plan has to exist before the order does.

7 MIG slices. One H100 can be split into up to seven MIG instances, which is how small jobs share a card without time-slicing.

> **The honest caveat:** these are H100 SXM figures. The PCIe card is 350 W with lower bandwidth, and H200 changes the memory numbers again. Read the spec sheet for the part you actually buy.

> **The lesson:** size the node from the card's real limits, not from the model's parameter count.

## In one line

> **Size the node, not the GPU.** These are H100 SXM figures. Check the card you buy.

**Read the spec**

```bash
nvidia-smi -q -d MEMORY
```
