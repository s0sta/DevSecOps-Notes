---
id: p508
title: "From kubectl apply to a routable service"
slug: from-kubectl-apply-to-a-routable-service
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, KubeProxy, CloudNative, DevOps]
source: "LinkedIn post P508 · Network series"
linkedin_date: 2029-12-25
design: timeline
---

# From kubectl apply to a routable service

You run kubectl apply, the Service appears, and for a few seconds every connection is refused. The object exists; the path to a pod does not yet.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **T+0s** | Service created | The API server assigns a ClusterIP and writes the object to etcd. |
| **T+1s** | Endpoints populated | The controller adds ready pod IPs to an EndpointSlice. |
| **T+2s** | kube-proxy notices | Every node watches Services and EndpointSlices, not just one. |
| **T+3s** | Rules written | iptables or IPVS rewrites the VIP to a pod IP and targetPort. |
| **T+4s** | First packet | The client hits the VIP; conntrack remembers the rewrite. |
| **T+5s** | Service ready | Readiness changes move the pod in and out; the rules follow. |

## Explained

### The object

Service created. The API server validates the Service, assigns a ClusterIP from the service CIDR, and writes it to etcd. The object is real, but no node has a rule for it yet.  
Endpoints populated. The endpoint slice controller, inside kube-controller-manager, watches matching pods and adds ready pod IPs to an EndpointSlice. A pod that is Running but not Ready stays out.

### The rules

Kube-proxy notices. Normally every node runs kube-proxy, and every kube-proxy watches Services and EndpointSlices. The update reaches all of them, not just the node running the pod.  
Rules written. In iptables mode, kube-proxy writes a chain that matches the ClusterIP and DNATs to a backend pod IP and targetPort. In IPVS mode it creates virtual and real servers. With no endpoints, iptables mode rejects instead.

### The packet

First packet. The client connects to ClusterIP:port. The node's rules rewrite the destination to a pod IP, conntrack remembers the mapping, and the reply is rewritten back.  
Ready. After that, readiness changes move the pod in and out of the slice, and the rules follow. The Service never sees a packet.

> **The honest caveat:** kube-proxy is not the only implementation. Cilium and Calico can replace it with eBPF or direct routing, so the rule order differs even when the result is the same.

> **The lesson:** a Service is a promise the data plane has to keep.

## In one line

> **The VIP is a rule, not a process.** A Service is a promise the data plane has to keep.

**Watch the slice**

```bash
kubectl get endpointslice -w
```
