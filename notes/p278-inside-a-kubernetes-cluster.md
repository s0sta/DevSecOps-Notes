---
id: p278
title: "Inside a Kubernetes cluster"
slug: inside-a-kubernetes-cluster
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Architecture, DevOps, CloudNative, SRE]
source: "LinkedIn post P278 · Visual series"
linkedin_date: 2028-07-06
design: architecture
---

# Inside a Kubernetes cluster

kubectl apply returns and the pod sits in Pending. The API server accepted the object, so the control plane looks fine; the work of turning that object into a running container is somewhere else.

## Quick reference

- **Control plane:** scheduler (SCHED) · API server (API) · etcd (KV) · controller manager (CTRL)
- **Workers:** kubelet (NODE) · container runtime (CRI) · kube-proxy (PROXY)
- **Add-ons:** CoreDNS (DNS) · CNI plugin (CNI)

**Request flow:** scheduler → API server → etcd; API server → kubelet → container runtime; kubelet → CoreDNS; kubelet → CNI plugin; API server → kube-proxy

## Explained

### Control plane

The control plane is four components. The API server is the front door and the only component that talks to etcd, the key-value store that holds cluster state. The scheduler watches for pods with no node and writes the binding back through the API server. The controller manager runs the controllers: Deployment, ReplicaSet, Node, each comparing desired state with actual.

### Workers

Each worker runs three things. The kubelet is the agent: it watches the API server for pods bound to its node and asks the container runtime to start them through the CRI. The runtime, usually containerd, pulls the image and runs the container. kube-proxy programs the iptables or IPVS rules that make Service virtual IPs work.

### Add-ons

Below the workers, the add-ons give the cluster names and addresses. CoreDNS runs on the workers and resolves service names inside the cluster. The CNI plugin assigns pod IPs and wires the pod network, and some plugins enforce network policy.

> **The honest caveat:** this is a logical map. A managed control plane hides those four boxes, CoreDNS runs on the workers rather than in its own tier, and the CNI is a set of binaries and daemons, not one service.

> **The lesson:** every cluster change is a write to the API server; every stuck object is a reconcile loop that cannot finish.

## In one line

> **Every pod starts at the API server.** Cluster state is a set of API writes, and etcd keeps them.

**Check the api**

```bash
kubectl get --raw /readyz
```
