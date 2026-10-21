---
id: p510
title: "Quiz: 3 Kubernetes network questions"
slug: quiz-3-kubernetes-network-questions
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, CKA, DevOps, CloudNative]
source: "LinkedIn post P510 · Network series"
linkedin_date: 2029-12-30
design: quiz
---

# Quiz: 3 Kubernetes network questions

Three questions separate people who have debugged a cluster from people who have only read about one. Answer before the reveal.

## Quick reference

**Q1. Why does a ClusterIP Service pass no traffic until it has endpoints?**

- a) The VIP only exists in node rules
- b) The API server drops traffic
- c) Pods must dial the VIP first

> **Answer:** a) The VIP only exists in node rules. A ClusterIP is virtual: no interface owns it. kube-proxy installs DNAT rules to endpoint IPs; with none, there is nowhere to send the packet, so it is rejected.

**Q2. What does kube-proxy actually program on each node?**

- a) iptables, IPVS or nftables rules
- b) A proxy process per Service
- c) The pod's network namespace

> **Answer:** a) iptables, IPVS or nftables rules. It writes DNAT and REJECT rules in iptables mode, or virtual and real servers in IPVS mode; nftables is the newer backend. It forwards no packets itself.

**Q3. Why does a NetworkPolicy need a CNI that enforces it?**

- a) The API server only stores the object
- b) Policies are applied by kubelet
- c) The scheduler reads the policy

> **Answer:** a) The API server only stores the object. NetworkPolicy is an API object; the apiserver stores it and filters nothing. A CNI plugin or mesh must translate it into rules. One that ignores it leaves pods open.

## Explained

### Question one

Why does a ClusterIP Service pass no traffic until it has endpoints? Because the VIP is virtual: no interface owns it and no process listens on it. kube-proxy, or the CNI that replaced it, writes DNAT rules that point at endpoint IPs. With no endpoints there is nowhere to rewrite the packet, so iptables mode rejects it. The Service object was never a server.

### Question two

What does kube-proxy program? In iptables mode it writes DNAT and REJECT rules; in IPVS mode it creates virtual servers and real servers; nftables is the newer backend. It does not proxy packets through a user-space process, and it does not touch the pod's network namespace. It keeps node rules in sync with Services and EndpointSlices.

### Question three

Why does a NetworkPolicy need a CNI that enforces it? Because the API server only stores the object. Policy is enforced where the packet is evaluated, at the veth, the bridge or an eBPF hook, and that is the CNI's code. A plugin that accepts the YAML and ignores it leaves every pod open, which is why a policy review is not a test.

> **The honest caveat:** a passing quiz is not a working cluster. The only proof is a connection that should fail and does.

> **The lesson:** know which component owns the drop.

## In one line

> **Rules need a reader.** A policy that nothing enforces is a comment with a schema.

**Test the deny**

```bash
kubectl exec -it api -- nc -vz db 5432
```
