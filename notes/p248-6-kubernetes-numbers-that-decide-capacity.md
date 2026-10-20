---
id: p248
title: "6 Kubernetes numbers that decide capacity"
slug: 6-kubernetes-numbers-that-decide-capacity
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CloudNative, SRE, DevOps, CapacityPlanning]
source: "LinkedIn post P248 · Platform series"
linkedin_date: 2028-04-27
design: numbers
---

# 6 Kubernetes numbers that decide capacity

Kubernetes capacity is not one number. It is a handful of defaults that decide how many pods fit, when they are evicted and how many failures you survive. Six numbers cover most of the argument.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **110** | Pods per node | The kubelet default maxPods. Plan pod CIDR and IPs around it. | default |
| **100m** | One CPU request | A tenth of a core. Requests, not limits, decide where a pod fits. | request |
| **100Mi** | Eviction threshold | The default memory.available floor before the kubelet evicts. | memory |
| **2** | Replicas minimum | One pod is a single point of failure. Two survive a rollout. | HA |
| **80%** | HPA CPU target | The default target. Above it, the HPA adds pods up to max. | HPA |
| **3** | Zones to spread | Three failure domains keep etcd quorum through one zone loss. | zones |

## Explained

### How many fit

110 pods per node. That is the kubelet default maxPods, and it bounds the pod CIDR, the IP plan and the room left for DaemonSets. A node with 110 pods needs addresses for all of them.  
100m CPU. A request of 100m is a tenth of a core. The scheduler adds requests, not limits, when it decides where a pod fits, so inflated requests waste a node before it is full.

### When it breaks

100Mi. The kubelet's default hard eviction threshold is memory.available<100Mi. Below that, it evicts pods to reclaim memory, starting with the lowest-priority ones.  
2 replicas. One pod is a single point of failure. Two survive a rolling update and a node drain; three survive a zone.

### How it scales

80 percent. The default HPA target for CPU utilisation. Above it, the HPA adds pods, up to maxReplicas and no further. A bad request makes the percentage lie.  
3 zones. Spread the control plane and workers across three failure domains. A three-member etcd cluster keeps quorum through one zone loss; two do not.

> **The honest caveat:** 110 is a kubelet default, not a promise. CNI plugins, IP prefixes and instance size all cap it lower.

> **The lesson:** capacity is a sum of defaults, so read them before you size a node.

## In one line

> **Defaults decide capacity.** Read them before you size a node or a namespace.

**Check a node**

```bash
kubectl describe node
```
