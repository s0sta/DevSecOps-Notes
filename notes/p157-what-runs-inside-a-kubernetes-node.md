---
id: p157
title: "What runs inside a Kubernetes node"
slug: what-runs-inside-a-kubernetes-node
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CloudNative, Linux, DevOps, Containers]
source: "LinkedIn post P157 · IT series"
linkedin_date: 2027-09-28
design: stack
---

# What runs inside a Kubernetes node

Kubernetes can feel like magic until you look inside a single worker node. It is just a Linux machine running a few agents. Here is what sits where.

## Quick reference

*Bottom to top: each layer runs the one above*

1. **The node** — A Linux machine, VM or bare metal, with CPU and RAM. · *Linux host*
2. **kubelet** — The agent that talks to the control plane and runs pods. · `kubelet`
3. **Container runtime** — Pulls images and runs containers for the kubelet. · *containerd*
4. **Pods** — Groups of containers the kubelet keeps alive. · *pods*
5. **Containers** — Your actual processes, isolated from each other. · *your app*
6. **kube-proxy** — Wires up Service networking so pods are reachable. · *networking*

## Explained

The node. At the bottom is an ordinary Linux machine, virtual or physical, with CPU, memory and disk. Everything above is software running on it, which is why node-level basics like patching, disk space and time sync still matter.

kubelet. The agent that makes the machine part of the cluster. It talks to the control plane, receives the list of pods it should run, starts and stops them, and reports their health back. If the kubelet is down, the node goes NotReady.

Container runtime. The kubelet does not run containers itself. It asks a runtime, usually containerd, to pull images and start containers. This is the layer that turns an image into a running process.

Pods. The runtime's containers are grouped into pods. The kubelet keeps each pod matching what the control plane asked for, restarting containers that crash.

Containers. Inside the pods are your actual processes, isolated from each other by Linux namespaces and cgroups, the same kernel features that power Docker.

kube-proxy. Finally, kube-proxy programs the node's networking rules so that Service addresses route to the right pods, wherever they run in the cluster.

Once you see that a node is Linux plus kubelet plus a runtime plus kube-proxy, kubectl describe node and node problems stop being mysterious.

## In one line

> **A node is just Linux with agents.** Demystify the node and Kubernetes stops being magic.

**Look at a node**

```bash
kubectl describe node <name>
```
