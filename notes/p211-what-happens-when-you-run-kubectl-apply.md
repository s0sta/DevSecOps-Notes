---
id: p211
title: "What happens when you run kubectl apply"
slug: what-happens-when-you-run-kubectl-apply
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CKA, CloudNative, DevOps, SRE]
source: "LinkedIn post P211 · Cloud / DevSecOps series"
linkedin_date: 2028-02-01
design: timeline
---

# What happens when you run kubectl apply

You run `kubectl apply -f app.yaml` and a pod appears. Between those two moments, the control plane does a precise sequence of work. Understanding it explains why Kubernetes is declarative, and where to look when a pod never starts.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **1** | kubectl sends it | Your YAML goes to the API server, authenticated. |
| **2** | Validated and stored | The API server checks it and writes it to etcd. |
| **3** | Controller notices | The deployment controller sees the desired state. |
| **4** | Scheduler picks a node | It chooses where the new pod should run. |
| **5** | kubelet starts it | The node's agent pulls the image and runs the container. |
| **6** | Status flows back | Health is reported up to etcd. kubectl get shows Running. |

## Explained

1. **kubectl sends it.** Your YAML is sent to the API server as a request, authenticated with your kubeconfig credentials and checked against RBAC. kubectl itself does not create anything; it just talks to the API server.

2. **Validated and stored.** The API server validates the object (is the YAML well-formed, do the fields exist, are you allowed?) and writes the desired state into etcd. At this point the object exists in the cluster's brain, but nothing is running yet.

3. **Controller notices.** The relevant controller, for a Deployment that is the deployment controller, is watching for changes. It sees the new desired state and creates the objects below it, a ReplicaSet, which in turn wants pods.

4. **Scheduler picks a node.** The new pods have no node assigned. The scheduler evaluates resources, taints, affinity and constraints, and binds each pod to a suitable node. A pod stuck in Pending usually means this step could not find a fit.

5. **kubelet starts it.** The kubelet on the chosen node sees a pod assigned to it, tells the container runtime to pull the image and start the container, and runs the probes.

6. **Status flows back.** The kubelet reports health up through the API server into etcd, and kubectl get pods shows Running.

The whole idea: you declare the goal, and independent controllers continuously converge reality toward it.

## In one line

> **You declare. The cluster converges.** apply sets the goal; controllers make it real.

**Watch it happen**

```bash
kubectl get pods -w
```
