---
id: p494
title: "Four reasons a packet is dropped"
slug: four-reasons-a-packet-is-dropped
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, VPC, NetworkSecurity, CloudComputing, DevOps]
source: "LinkedIn post P494 · Network series"
linkedin_date: 2029-11-22
design: explainer
---

# Four reasons a packet is dropped

A dropped packet is not a mystery. It met a rule, a route or a missing target, and the VPC has only four places for that to happen.

## Quick reference

### Security group

- Stateful: the reply is allowed
- Allow rules only, no deny
- Checked at the network interface
- No matching rule means drop

### Network ACL

- Stateless: each direction alone
- Ordered rules, lowest wins
- Needs an ephemeral-port rule
- Applies to the whole subnet

### Missing route

- Longest prefix match decides
- No match means a drop
- Peering routes are not transitive
- Add the route on both sides

### Blackhole

- Target deleted, route stayed
- State shows as blackhole
- Common after a NAT is removed
- The log may show ACCEPT, then silence

> **Note:** The order matters: interface, subnet, route, target. Stop at the first one that says no.

## Explained

### At the interface

Security group first. It is stateful, allow-only and evaluated at the network interface. If no rule allows the traffic, it is dropped, and the reply to an allowed connection is allowed automatically.

Network ACL second. It is stateless, ordered by rule number and attached to the subnet. Return traffic needs its own rule, which is why an inbound 443 rule without an outbound 1024-65535 rule produces a one-way connection.

### On the path

Missing route third. Every subnet uses one route table; the longest prefix wins, and no matching route means a drop. There is no fallback to the default when nothing matches. Peering routes are not transitive and must exist on both sides.

Blackhole fourth. The route is still in the table but its target is gone, so its state turns to blackhole and the packet is dropped. A deleted NAT gateway or network interface leaves exactly this. The table still looks populated, which is why blackholes survive so many reviews.

> **The honest caveat:** a flow log records what reached the interface, not why the router dropped it. A missing route or a blackhole can leave an ACCEPT record and no reply.

> **The lesson:** the packet tells you where it died; the order tells you where to look.

## In one line

> **Every drop has a reason.** The packet did not vanish; a rule, a route or a deleted target did it.

**Watch the drop**

```bash
aws ec2 describe-flow-logs
```
