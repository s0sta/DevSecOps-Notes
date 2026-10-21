---
id: p504
title: "The four service types"
slug: the-four-service-types
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, CloudNative, DevOps, SRE]
source: "LinkedIn post P504 · Network series"
linkedin_date: 2029-12-16
design: explainer
---

# The four service types

You need to expose a service and the YAML offers four types. One is the trunk, two build on it, and one is only a DNS record.

## Quick reference

### ClusterIP

- A virtual IP from the service CIDR
- Reachable inside the cluster only
- The default type for every Service

### NodePort

- One port on every node, 30000-32767
- Still builds a ClusterIP behind it
- For demos and bare-metal edge cases

### LoadBalancer

- NodePort plus a cloud load balancer
- A public or internal address, for a fee
- One load balancer per Service by default

### ExternalName

- A DNS CNAME, not a proxy or a VIP
- No endpoints and no kube-proxy rules
- For a managed service outside the cluster

> **Note:** Two types build on ClusterIP; ExternalName is only a DNS name.

## Explained

### Inside the cluster

ClusterIP is the default and the type NodePort and LoadBalancer build on. The API server assigns a virtual IP from the service CIDR, and kube-proxy installs rules that rewrite traffic to a ready pod. Nothing listens on the VIP, so a curl only works while endpoints exist.

### From outside

NodePort opens one port on every node, by default in 30000-32767, and forwards it to the same ClusterIP. It is quick for a demo, but it exposes the port on every node with a public address. LoadBalancer asks the cloud controller for an external load balancer that targets those NodePorts. It gives you an address and health checks, and it bills per Service. On bare metal it stays pending until MetalLB answers.

### A name, not a proxy

ExternalName is the odd one: it returns a CNAME record and creates no endpoints, no VIP and no proxy. Clients resolve the name and connect directly, which is useful for a managed database and useless if you expect policy or TLS termination.

> **The honest caveat:** a LoadBalancer Service is only as portable as its cloud controller. The same YAML on a laptop or a bare-metal cluster will sit in pending until a controller implements it.

> **The lesson:** choose the smallest exposure that works, then put one ingress in front of the rest.

## In one line

> **Pick the smallest path that works.** Every type above ClusterIP adds a hop someone must operate.

**Check the type**

```bash
kubectl get svc -o wide
```
