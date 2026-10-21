---
id: p502
title: "Pod-to-pod networking, drawn"
slug: pod-to-pod-networking-drawn
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, CNI, CloudNative, DevOps]
source: "LinkedIn post P502 · Network series"
linkedin_date: 2029-12-11
design: architecture
---

# Pod-to-pod networking, drawn

Two pods on the same node keep talking after the node loses its default route. Their packets never leave the host: the path is a veth pair and a bridge.

## Quick reference

- **Pod a:** Pod A (POD) · veth pair A (VETH)
- **Node:** cni0 bridge (BRDG) · CNI plugin (CNI)
- **Pod b:** veth pair B (VETH) · Pod B (POD)

**Request flow:** Pod A → veth pair A → cni0 bridge → veth pair B → Pod B; CNI plugin → cni0 bridge

## Explained

### The pod side

Pod A has an eth0 inside its network namespace. That interface is one end of a veth pair; the other end sits in the host namespace and attaches to cni0. The pod gets an IP from the node's pod CIDR and a default route that points at the host.

### The node

On the host, cni0 forwards frames by MAC address between the two host veths. No routing, no NAT and no kube-proxy: pod IP to pod IP is a layer 2 hop. The CNI plugin beside it did the wiring: it allocated the pod IP, created the veth pair, attached it to the bridge, and enforces NetworkPolicy at that boundary. If the pods sit on different nodes, the CNI encapsulates the packet or routes the pod CIDR; the bridge path stops at the node boundary.

### The other end

Pod B mirrors Pod A: its own eth0, its own veth pair, and a host end on the same bridge. The reply walks the same path backwards.

> **The honest caveat:** not every CNI uses a bridge. Cilium attaches eBPF programs to the veth and Calico can route pod IPs directly, so the cni0 box is the common diagram, not a law.

> **The lesson:** the pod IP stays the same; the path under it is the CNI's choice.

## In one line

> **Two pods, one layer 2 hop.** The pod IP never changes; the path under it does.

**Trace the path**

```bash
kubectl exec -it api -- ip route
```
