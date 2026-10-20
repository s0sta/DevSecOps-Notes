---
id: p298
title: "The four Kubernetes objects you actually use, drawn"
slug: the-four-kubernetes-objects-you-actually-use-drawn
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CloudNative, DevOps, CKA, PlatformEngineering]
source: "LinkedIn post P298 · Visual series"
linkedin_date: 2028-08-22
design: explainer
---

# The four Kubernetes objects you actually use, drawn

A new team asks where to put the port, the TLS certificate and the database URL. Four objects answer most of it, and every other kind is a variation.

## Quick reference

### Deployment

- Runs pods and replaces them when they die
- Rolling update, then a clean rollback
- Replicas live here, not in the pod
- Pod names are random on purpose

### Service

- One stable name and IP for the pods
- Label selector decides the endpoints
- ClusterIP inside, LoadBalancer outside
- kube-proxy programs the routing rules

### Ingress

- Routes HTTP requests by host and path
- Needs a controller, or it does nothing
- TLS usually ends at the controller
- One entry point for many services

### ConfigMap / Secret

- ConfigMap holds plain settings
- Secret holds base64, not encryption
- Mount as files or inject as env vars
- Editing one does not restart pods

> **Note:** A Secret is base64, not encryption. Turn on encryption at rest and keep RBAC tight.

## Explained

### Deployment

A Deployment runs pods and replaces them. You declare an image and a replica count; the controller creates a ReplicaSet, which creates pods with random names, and a rolling update swaps them without downtime. Rollback is a revision, not a rebuild.

### Service

A Service gives those pods one stable name and IP. The label selector decides which pods are endpoints, and kube-proxy programs the routing. ClusterIP is internal, NodePort opens a port on every node, and LoadBalancer asks the cloud for one.

### Ingress

An Ingress routes HTTP by host and path to services. It is only a spec: without a controller running, it does nothing. TLS usually ends at the controller, not at the pod.

### ConfigMap and Secret

A ConfigMap holds plain settings; a Secret holds base64 values Kubernetes treats more carefully. Both mount as files or inject as environment variables, and changing either does not restart a running pod.

> **The honest caveat:** a Secret is encoded, not encrypted. Encryption at rest and RBAC are separate settings, and a readable namespace turns a Secret into a password with extra steps.

> **The lesson:** each object answers one question. What runs, how it is reached, how it is routed, and what it is told.

## In one line

> **Four objects. Most of the cluster.** Learn these and every other kind is a variation.

**List the four**

```bash
kubectl get deploy,svc,ing,cm -A
```
