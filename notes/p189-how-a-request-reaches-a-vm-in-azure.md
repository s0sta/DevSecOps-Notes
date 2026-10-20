---
id: p189
title: "How a request reaches a VM in Azure"
slug: how-a-request-reaches-a-vm-in-azure
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [Azure, AZ104, Networking, CloudComputing, CyberSecurity]
source: "LinkedIn post P189 · Cloud / DevSecOps series"
linkedin_date: 2027-12-12
design: pipeline
---

# How a request reaches a VM in Azure

When you cannot reach a VM in Azure, the problem is almost always one specific layer between the user and the app. Knowing the path turns guesswork into a checklist, and it is core AZ-104 networking.

## Quick reference

1. **DNS resolves** — The name points to a public IP or load balancer. · *DNS*
2. **Public IP / Load Balancer** — Traffic enters the Azure network here. · *frontend*
3. **NSG on the subnet** — Allow/deny rules filter by IP and port. · *NSG*
4. **NSG on the NIC** — A second NSG can filter per VM. · *NIC rules*
5. **The VM's OS firewall** — ufw or firewalld still applies inside. · `host firewall`
6. **The app listens** — Only now does your service see the request. · `:443`

## Explained

1. **DNS resolves.** The domain name points to a public IP or a load balancer's address. A wrong or missing DNS record means nothing after this matters, and it is the first thing to check.

2. **Public IP or Load Balancer.** This is where traffic enters the Azure network. A load balancer also has its own health probes and rules; if the backend is marked unhealthy, it stops sending traffic there.

3. **NSG on the subnet.** The first set of allow and deny rules, applied to the whole subnet. If there is no rule allowing your port from the source, the packet is dropped here, silently.

4. **NSG on the NIC.** Azure lets you attach a second NSG directly to a VM's network interface. Both the subnet and NIC NSGs must allow the traffic, which catches people out: the subnet allows it, but the NIC does not.

5. **The VM's OS firewall.** Inside the VM, ufw or firewalld still applies. The Azure layers can all say yes and the host firewall still say no.

6. **The app listens.** Only now does your service actually receive the request, and only if it is bound to the right address and port.

The debugging order: DNS, then the load balancer health, then both NSGs, then the host firewall, then the app. Walk it in order and the broken gate reveals itself.

## In one line

> **Many gates, one request.** 'Can't reach the VM' is one of these layers saying no.

**Trace the layers:** check DNS, then NSG rules, then the host firewall
