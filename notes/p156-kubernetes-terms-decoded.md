---
id: p156
title: "Kubernetes terms, decoded"
slug: kubernetes-terms-decoded
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CloudNative, DevOps, Containers, ITCareer]
source: "LinkedIn post P156 · IT series"
linkedin_date: 2027-09-26
design: reveal
---

# Kubernetes terms, decoded

Kubernetes is not conceptually hard. The vocabulary is what makes it feel impossible at first. Six terms you will meet on day one, in plain English.

## Quick reference

- **Pod** — The smallest unit you run: one or more containers that share a network and live and die together.
- **Deployment** — Describes the desired state: which image and how many replicas. It keeps reality matching that.
- **Service** — A stable address and load balancer for a set of pods, even as pods come and go.
- **Ingress** — Routes outside HTTP traffic to services by host and path. The front door of the cluster.
- **ConfigMap** — Configuration kept outside the image, injected into pods as files or variables.
- **Namespace** — A way to divide one cluster into separate areas for teams or environments.

## Explained

Pod. The smallest thing Kubernetes runs. Usually one container, sometimes a few that belong together and share a network address and storage. Pods are disposable: they are created and destroyed constantly, and you rarely manage them directly.

Deployment. A description of what you want: this image, this many replicas. Kubernetes then works to make reality match, creating pods, replacing crashed ones, and rolling out new versions. You change the Deployment; it handles the pods.

Service. Pods come and go and get new IP addresses, so you cannot rely on a pod's address. A Service gives a stable name and address, and load-balances across whichever pods currently match it. This is how parts of your app find each other.

Ingress. Routes outside HTTP and HTTPS traffic into the cluster, choosing a Service based on the host name and URL path. It is the front door, and where TLS certificates usually live.

ConfigMap. Configuration kept outside the container image and injected into pods as environment variables or files. Its sibling, a Secret, does the same for sensitive values. This keeps one image usable across environments.

Namespace. Divides a single cluster into separate areas, for teams or for dev, staging and prod, each with its own names and limits.

Once these six click, most Kubernetes documentation suddenly reads easily.

## In one line

> **The words are the hard part.** The concepts are simple once the names click.

**See them all**

```bash
kubectl get pods,svc,ingress -A
```
