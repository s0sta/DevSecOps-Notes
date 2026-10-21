---
id: p509
title: "The layers a pod packet crosses"
slug: the-layers-a-pod-packet-crosses
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Networking, CNI, CloudNative, Linux]
source: "LinkedIn post P509 · Network series"
linkedin_date: 2029-12-27
design: stack
---

# The layers a pod packet crosses

A pod on node A calls a pod on node B, and the packet crosses six layers. Most debugging stops early.

## Quick reference

*Bottom to top: the path a packet takes*

1. **veth pair** — eth0 in the pod pairs with a host veth; every packet crosses it. · *VETH*
2. **Linux bridge** — cni0 forwards by MAC to the host veth, or passes it to the host stack. · *BRIDGE*
3. **CNI overlay** — VXLAN, IPIP or routed pod CIDRs carry it to the next node. · *OVERLAY*
4. **node route** — The host table picks the interface, the next hop and the MTU. · *ROUTE*
5. **underlay** — The physical or cloud network moves the packet, unaware of pods. · *UNDERLAY*
6. **destination pod** — The far node decapsulates, bridges and passes it into the pod netns. · *NETNS*

## Explained

### The pod end

Veth pair. Inside the pod, eth0 is one end of a veth pair; the peer sits in the host namespace and carries every packet out. The pod's default route points at the host side.  
Linux bridge. On a typical CNI, the host veth is attached to cni0 or another Linux bridge. The bridge forwards by MAC to the right port, or passes the frame to the host stack.

### The cluster network

CNI overlay. When the destination is on another node, the CNI decides how to carry the packet. VXLAN and IPIP wrap it in an outer header; routed CNIs advertise the pod CIDR with BGP.  
Node route. The host routing table chooses the interface and next hop. This is where the MTU is set, and where a wrong MTU makes large packets vanish while small pings work.

### The far side

Underlay. The physical or cloud network forwards it without knowing what a pod is. Security groups and ACLs here can drop traffic the cluster allows.  
Destination pod. The far node decapsulates, routes or bridges to the destination host veth, and the packet enters the pod netns. Only now does the application see it.

> **The honest caveat:** eBPF CNIs collapse several layers. Cilium can attach to the veth and route directly, so the bridge may not exist; the failure modes move, they do not disappear.

> **The lesson:** know which layer owns the drop before you change a manifest.

## In one line

> **Every layer has a failure mode.** Know which layer owns the drop before you change a manifest.

**Check the mtu**

```bash
ping -M do -s 1400 <pod-ip>
```
