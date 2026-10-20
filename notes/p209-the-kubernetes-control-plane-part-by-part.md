---
id: p209
title: "The Kubernetes control plane, part by part"
slug: the-kubernetes-control-plane-part-by-part
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CKA, CloudNative, DevOps, SRE]
source: "LinkedIn post P209 · Cloud / DevSecOps series"
linkedin_date: 2028-01-27
design: stack
---

# The Kubernetes control plane, part by part

Kubernetes feels like magic until you see the control plane, the handful of components that make a cluster self-healing. Each has one job, and together they turn your desired state into reality. This is core CKA material.

## Quick reference

*The brain of the cluster*

1. **API server** — The front door. Everything talks to it, nothing bypasses it. · *kube-apiserver*
2. **etcd** — The database. The cluster's entire state lives here. · *etcd*
3. **Scheduler** — Decides which node each new pod runs on. · *kube-scheduler*
4. **Controller manager** — Drives reality toward your desired state. · *controllers*
5. **Cloud controller** — Talks to the cloud for load balancers and disks. · *cloud-cm*
6. **kubelet (on nodes)** — The agent that actually runs the pods. · `kubelet`

## Explained

API server (kube-apiserver). The front door. Every command, every component, every kubectl call goes through it, and nothing talks to etcd directly. It validates requests, handles authentication and authorisation, and is the only component that reads and writes the datastore. If the API server is down, the cluster is effectively frozen.

etcd. The database. The entire state of the cluster, every object, its spec and status, lives in etcd as key-value data. This is why backing up etcd is backing up the cluster, and why etcdctl snapshot save is a classic exam task.

Scheduler (kube-scheduler). When a new pod has no node yet, the scheduler picks one, based on resources, taints, affinity and constraints. It decides where, not how.

Controller manager. A bundle of controllers, each watching for a difference between desired and actual state and acting to close it: the deployment controller creates ReplicaSets, the node controller notices dead nodes. This control loop is the heart of Kubernetes.

Cloud controller manager. Talks to the cloud provider for things like load balancers, routes and persistent disks, keeping cloud-specific logic separate.

kubelet. On each worker node, the agent that actually starts and watches the pods the control plane assigned.

The whole idea in one line: you declare desired state, and the control plane continuously works to make reality match.

## In one line

> **Desired state in, reality out.** The control plane's whole job is to close that gap.

**Back up the brain**

```bash
etcdctl snapshot save snap.db
```
