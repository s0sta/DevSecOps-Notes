---
id: p316
title: "A GPU training cluster, drawn"
slug: a-gpu-training-cluster-drawn
sections: [devsecops]
topic: "AI infrastructure & LLM security"
tags: [GPU, AIInfrastructure, HPC, InfiniBand, MachineLearning]
source: "LinkedIn post P316 · Visual series"
linkedin_date: 2028-10-03
design: architecture
---

# A GPU training cluster, drawn

You rent a rack of GPUs and the job finishes no faster than a single node. The cards are fine; the path between them is not.

## Quick reference

- **Tier 1 · Control:** API server (API) · Scheduler (SCHED)
- **Tier 2 · Fabric:** InfiniBand (IB) · NVLink (NV)
- **Tier 3 · Compute:** GPU nodes (GPU) · Storage (IO)

**Request flow:** API server → Scheduler → InfiniBand → GPU nodes → Storage; NVLink → GPU nodes

**Around it:** Checkpoint store (CKPT) · Telemetry (DCGM) · Registry (REG) · Identity (IAM)

## Explained

### Control

A job reaches the cluster through the API server, which authenticates the user and records the request. The scheduler places it: which nodes, how many GPUs each, where the ranks land. Placement is the performance decision, because a rank on the wrong side of the fabric waits for its pair.

### Fabric

InfiniBand connects the nodes, and NVLink connects the GPUs inside one node. Both matter, and they are not the same: a collective that stays inside a node uses NVLink, and every step that crosses nodes pays the InfiniBand hop. A cluster with fast cards and a thin fabric is a set of fast islands.

### Compute

The GPU nodes run the job. Local storage holds the dataset shard and the checkpoints in flight; the shared storage tier holds what must survive the node. A node that cannot feed its cards is idle with a full queue behind it.

Around the tiers: a checkpoint store for restarts, telemetry that samples the cards, a registry for the image, and identity for every job. These are the parts nobody demos and every long job needs.

> **The honest caveat:** a faster fabric will not fix a data loader that cannot keep up, and utilisation alone does not tell you whether the maths is useful.

> **The lesson:** size the fabric and the storage for the job, not just the cards on the invoice.

## In one line

> **The network is the cluster.** You buy GPUs; the fabric decides whether they act like one machine.

**Check the links**

```bash
nvidia-smi topo -m
```
