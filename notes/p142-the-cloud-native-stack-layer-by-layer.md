---
id: p142
title: "The cloud-native stack, layer by layer"
slug: the-cloud-native-stack-layer-by-layer
sections: [devsecops]
topic: "Kubernetes"
tags: [CloudNative, Kubernetes, DevOps, Containers, CloudComputing]
source: "LinkedIn post P142 · IT series"
linkedin_date: 2027-08-24
design: stack
---

# The cloud-native stack, layer by layer

People say "cloud-native" as if it is one thing. It is really a stack of layers, each running on the one below. Knowing them tells you where a problem lives and where to harden.

## Quick reference

*Bottom to top: each layer runs on the one below*

1. **Cloud / hardware** — The datacenter: compute, storage and network you rent. · *IaaS*
2. **Linux host** — The operating system on each node. Patched and hardened. · `Ubuntu / RHEL`
3. **Container runtime** — Runs the containers. Images become processes. · *containerd*
4. **Kubernetes** — Schedules containers across nodes, heals and scales them. · *orchestration*
5. **Service mesh** — Secures and routes traffic between services. Optional. · *mTLS + routing*
6. **Your app** — Containers, config and secrets. The part users touch. · *pods + config*

## Explained

Cloud or hardware. The foundation: the compute, storage and network you rent from a provider, or run yourself. This is IaaS, and everything above depends on it being available and correctly configured.

Linux host. Every node runs an operating system, almost always Linux. It still needs patching, hardening, time sync and enough disk. People forget this layer exists once Kubernetes is on top, and that is where quiet problems start.

Container runtime. The piece that actually runs containers, turning an image into an isolated process. These days it is usually containerd. You rarely touch it directly, but when images will not start, this is a layer to check.

Kubernetes. The orchestrator. It schedules containers across nodes, restarts them when they crash, scales them with load, and reschedules them when a node dies. This is the layer that makes the system self-healing.

Service mesh. Optional, but common at scale. It handles secure, encrypted traffic between services, retries, and fine-grained routing, without each app implementing it. mTLS between services lives here.

Your app. Containers, their config and their secrets. The only layer your users actually experience.

The key insight: each layer trusts the one beneath it. A compromised node or an unpatched host undermines every clever thing Kubernetes does above it. Security and reliability are only as strong as the lowest layer.

## In one line

> **Each layer trusts the one below.** A weak lower layer undermines everything above it.

**See the bottom layers**

```bash
kubectl get nodes -o wide
```
