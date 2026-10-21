---
id: p503
title: "The Kubernetes network debugging cheat sheet"
slug: the-kubernetes-network-debugging-cheat-sheet
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, Troubleshooting, DevOps, SRE]
source: "LinkedIn post P503 · Network series"
linkedin_date: 2029-12-13
design: cheatsheet
---

# The Kubernetes network debugging cheat sheet

A service is down, the pod is Running, and the logs are clean. The network is now a process of elimination, and these four blocks are the order I use.

## Quick reference

### DNS

```bash
kubectl exec -it api -- nslookup db
kubectl exec api -- cat /etc/resolv.conf
kubectl get svc -n kube-system kube-dns
kubectl -n kube-system get pods
kubectl exec api -- nslookup kubernetes
```

### Sockets

```bash
kubectl exec -it api -- ss -tlnp
kubectl exec -it api -- ss -tan
kubectl exec -it api -- ss -s
kubectl exec -it api -- netstat -tulpn
kubectl port-forward svc/api 8080:80
```

### Policy

```bash
kubectl get netpol -A
kubectl describe netpol api
kubectl get pods --show-labels
kubectl exec -it api -- nc -vz db 5432
kubectl get netpol api -o yaml
```

### Trace

```bash
kubectl exec -it api -- tcpdump -i eth0
kubectl exec -it api -- tcpdump -n port 53
kubectl exec -it api -- ping -c 3 db
kubectl debug -it api --image=busybox
kubectl exec -it api -- ip route
```

## Explained

### DNS

Start with the name. nslookup db from inside the pod proves the resolver and the search path; `cat /etc/resolv.conf` shows the nameserver and ndots the pod actually got. If the name fails, everything after it is noise.

### Sockets

If the name resolves, check the listener. `ss -tlnp` shows what is bound and on which address; `ss -tan` adds the connection states. A process bound to 127.0.0.1 is unreachable from another pod, which is the most common "the port is open" lie.

### Policy

A refused connection can be a NetworkPolicy, not a dead app. List the policies, read the selectors, and compare them with the pod labels. Then test the exact pair the policy should allow; a policy that selects no pods enforces nothing.

### Trace

When the path is still unclear, capture. tcpdump on eth0 shows whether the SYN left the pod, and a reply proves the far side heard it. ping and ip route answer the layer 3 questions, and kubectl debug gives you a shell with the tools the app image lacks.

> **The honest caveat:** many app images have no ss, dig or tcpdump. Run the checks from a debug container or a netshoot pod, and remember that a missing binary looks like a failed command.

> **The lesson:** debug in the order the packet travels, not the order the tools appear.

## In one line

> **Find the hop, not the blame.** Four blocks, one order: name, socket, policy, packet.

**Run it in the pod**

```bash
kubectl exec -it api -- ss -tlnp
```
