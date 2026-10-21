---
id: p424
title: "Canary, blue-green and rolling, drawn"
slug: canary-blue-green-and-rolling-drawn
sections: [devsecops]
topic: "Release & build engineering"
tags: [DevOps, ReleaseEngineering, Kubernetes, ProgressiveDelivery, SRE]
source: "LinkedIn post P424 · DevOps series"
linkedin_date: 2029-06-12
design: explainer
---

# Canary, blue-green and rolling, drawn

The deployment strategy decides how much damage a bad build can do. Rolling, blue-green and canary answer that question differently.

## Quick reference

### Rolling update

- Replaces instances in batches
- No extra environment, needs surge capacity
- Rollback is another rollout, not instant
- The Kubernetes default for stateless apps

### Blue-green

- Two identical environments, one router
- The switch sends all traffic at once
- Rollback is a switch back in seconds
- Costs double capacity at cutover

### Canary

- A small share of real traffic goes first
- Compare errors and latency to stable
- Raise the share only when the numbers hold
- Needs traffic splitting and metrics

### When each fits

- Rolling: stateless, schema-compatible
- Blue-green: instant switch, spare capacity
- Canary: high traffic, risky change, metrics
- All three need a signal you trust

> **Note:** The strategy decides how much risk you take before you know.

## Explained

### Rolling

A rolling update replaces instances in batches. Kubernetes starts new pods, waits for readiness, then removes old ones, so versions overlap. It needs no second environment, only surge capacity, and the default is a quarter of the replicas at a time. Rollback is another rolling update in reverse, which is safe but not instant.

### Blue-green

Blue-green runs two identical environments. Blue serves all traffic while green receives the new release and its smoke tests; then the router switches, and rollback is a switch back. The switch is instant, the cost is double capacity at cutover, and the shared database is where most plans meet reality.

### Canary

A canary sends a small share of real traffic to the new version, compares error rate and latency against the stable baseline, then raises the share. That comparison needs traffic splitting and metrics good enough to separate signal from noise.

### Choosing

Rolling fits stateless services with a compatible schema. Blue-green fits when the switch must be instant and you can pay for two environments. Canary fits high-traffic changes where a small exposure is cheaper than a big one.

> **The honest caveat:** a canary on a low-traffic endpoint can run for hours without enough requests to prove anything. It is only as good as the traffic it sees.

> **The lesson:** choose by how fast you can see a failure, not by which one looks modern.

## In one line

> **Route traffic by evidence.** Three strategies, one question: how fast can you see a bad release?

**Advance the canary**

```bash
kubectl argo rollouts promote api
```
