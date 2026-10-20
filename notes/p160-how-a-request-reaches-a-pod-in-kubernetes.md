---
id: p160
title: "How a request reaches a pod in Kubernetes"
slug: how-a-request-reaches-a-pod-in-kubernetes
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, CloudNative, DevOps, SRE]
source: "LinkedIn post P160 · IT series"
linkedin_date: 2027-10-05
design: pipeline
---

# How a request reaches a pod in Kubernetes

A user opens your app running in Kubernetes. Between the browser and the container, the request passes through several layers. When something is "not reachable", knowing them turns a vague problem into a specific one.

## Quick reference

1. **DNS and the load balancer** — The name resolves to the cluster's entry point. · *LB*
2. **Ingress controller** — Matches host and path, terminates TLS. · *ingress*
3. **Service** — A stable address for a changing set of pods. · *service*
4. **kube-proxy rules** — Picks one healthy pod and routes to it. · *endpoints*
5. **The pod** — The request arrives at a container. · *pod*
6. **Readiness decides** — Only ready pods are ever chosen. · *readiness*

## Explained

1. **DNS and the load balancer.** The domain resolves to the cluster's entry point, usually a cloud load balancer in front of the cluster. If DNS is wrong or the load balancer has no healthy targets, nothing after this matters.

2. **Ingress controller.** The load balancer forwards to the ingress controller, which reads the host name and URL path and decides which Service should handle the request. This is also where TLS is usually terminated. A missing or wrong ingress rule sends traffic nowhere, or to the wrong app.

3. **Service.** The ingress targets a Service, which is a stable address for a set of pods that are constantly being created and destroyed. The Service does not care which pods exist right now; it tracks them by label.

4. **kube-proxy rules.** On each node, kube-proxy has programmed networking rules that pick one healthy pod behind the Service and route the request to it, load-balancing across them.

5. **The pod.** The request finally reaches a container inside a pod, where your code runs and responds.

6. **Readiness decides.** Throughout, only pods that pass their readiness probe are in the Service's list of endpoints. This is why a pod can be Running but get no traffic: it is not ready.

Debugging tip: walk the chain with kubectl get ingress, svc and endpoints. An empty endpoints list means no ready pods, and that points straight at the problem.

## In one line

> **Many hops, one request.** Know the hops, and 'it is not reachable' gets specific.

**Trace the chain**

```bash
kubectl get ingress,svc,endpoints
```
