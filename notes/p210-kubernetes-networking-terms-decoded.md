---
id: p210
title: "Kubernetes networking terms, decoded"
slug: kubernetes-networking-terms-decoded
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CKA, Networking, CloudNative, DevOps]
source: "LinkedIn post P210 · Cloud / DevSecOps series"
linkedin_date: 2028-01-30
design: reveal
---

# Kubernetes networking terms, decoded

Kubernetes networking is where most people get lost, and it is a big part of the CKA. Six terms, in plain English, that make cluster traffic make sense.

## Quick reference

- **ClusterIP** — The default Service type: a stable internal address, reachable only inside the cluster.
- **NodePort** — Opens the same port on every node, so traffic from outside can reach a Service.
- **LoadBalancer** — Asks the cloud for an external load balancer in front of a Service.
- **Ingress** — Routes outside HTTP traffic to Services by host and path. One entry point, many apps.
- **CNI** — The plugin (Calico, Cilium, Flannel) that gives every pod an IP and wires the network.
- **NetworkPolicy** — A firewall for pods: which pods may talk to which. Default is allow-all until you add one.

## Explained

ClusterIP. The default Service type. It gives a set of pods one stable internal IP and DNS name, load-balanced, reachable only from inside the cluster. This is how your services find each other: the frontend talks to backend, not to a pod IP that changes.

NodePort. Opens the same high port (30000 to 32767) on every node, forwarding to a Service. It is the simplest way to reach something from outside the cluster, and common in labs, though rarely the final answer in production.

LoadBalancer. Asks the cloud provider to create an external load balancer with a public IP in front of a Service. This is the usual production way to expose a single service to the internet.

Ingress. Routes outside HTTP and HTTPS traffic to different Services based on host name and URL path, so one entry point and one IP can serve many apps, with TLS in one place. An Ingress needs an ingress controller running to do the work.

CNI. The Container Network Interface plugin, like Calico, Cilium or Flannel, that actually gives every pod an IP address and connects them. Your choice of CNI affects performance and which features, like NetworkPolicy, you get.

NetworkPolicy. A firewall for pods: rules for which pods may talk to which, on which ports. The catch: by default Kubernetes allows all pod-to-pod traffic. A NetworkPolicy only takes effect once you add one, and your CNI must support it.

## In one line

> **Pods, Services, and the rules between.** Networking is where most Kubernetes confusion lives.

**See the services**

```bash
kubectl get svc,ingress -A
```
