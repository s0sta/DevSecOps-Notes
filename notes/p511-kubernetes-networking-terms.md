---
id: p511
title: "Kubernetes networking terms"
slug: kubernetes-networking-terms
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, CNI, CloudNative, DevOps]
source: "LinkedIn post P511 · Network series"
linkedin_date: 2030-01-01
design: reveal
---

# Kubernetes networking terms

Six terms carry most Kubernetes networking conversations, and most arguments come from mixing two of them.

## Quick reference

- **CNI** — The plugin contract that gives a pod an interface, an IP and routes, then removes them.
- **ClusterIP** — A virtual IP from the service CIDR; node rules rewrite traffic to a ready pod.
- **NodePort** — A port on every node that forwards to the Service, still behind a ClusterIP.
- **Ingress** — An L7 routing object: host and path rules handled by a controller, not the API server.
- **NetworkPolicy** — A label-selected allow-list for pods; only a CNI that implements it enforces it.
- **kube-proxy** — The node agent that programs iptables, IPVS or nftables rules for Services.

## Explained

### The plugin

CNI is the interface between the kubelet and the network plugin: give this pod an interface, an IP and routes, and remove them when it dies. The plugin, not Kubernetes, owns the data plane.

### The service path

ClusterIP is a virtual IP from the service CIDR. No process owns it; node rules rewrite traffic to a ready pod. NodePort opens a port on every node and forwards to that same VIP; it is another path, not another backend.

### The entry and the policy

Ingress is an L7 routing object: host and path rules handled by a controller, not by the API server. It terminates or passes TLS, and it needs a controller and a Service behind it.  
NetworkPolicy is a label-selected allow-list for pods. It is stored by the API server and enforced by the CNI, so a plugin that ignores it leaves the pods open.

### The agent

kube-proxy is the node agent that programs iptables, IPVS or nftables rules for Services. Many clusters now replace it with eBPF, but the job remains: turn Service and EndpointSlice objects into packet rules.

> **The honest caveat:** these definitions are the common case, not the specification. Implementations differ, and the only reliable answer is the one your cluster's data plane actually enforces.

> **The lesson:** name the layer before you argue about the fix.

## In one line

> **Know the term, then check the rules.** A named layer is easier to test than a vague suspicion.

**Read the rules**

```bash
kubectl get netpol -A
```
