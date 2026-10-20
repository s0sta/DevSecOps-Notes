---
id: p287
title: "VPC anatomy, drawn"
slug: vpc-anatomy-drawn
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, Networking, VPC, CloudArchitecture, DevOps]
source: "LinkedIn post P287 · Visual series"
linkedin_date: 2028-07-27
design: explainer
---

# VPC anatomy, drawn

A VPC looks like a diagram and behaves like a set of rules. Four parts decide whether a packet gets in, gets out or goes nowhere.

## Quick reference

### Subnets

- One subnet lives in one availability zone
- Public means a route to an internet gateway
- AWS reserves five addresses in every subnet
- A private subnet has no inbound route

### Route tables

- The local route for the VPC CIDR cannot be deleted
- Longest prefix match chooses the next hop
- Each subnet follows exactly one table
- 0.0.0.0/0 is the route that makes it public

### Internet and NAT

- An internet gateway attaches to the VPC
- A NAT gateway gives outbound access only
- Nothing unsolicited gets in through NAT
- The NAT gateway lives in a public subnet

### Security groups and NACLs

- Security groups are stateful and allow-only
- NACLs are stateless and can deny traffic
- A group sits on an ENI, a NACL on a subnet
- NACL rules run in order, first match wins

> **Note:** Stateful means the reply is allowed; stateless means you write both directions.

## Explained

**Subnets**  
A subnet is one CIDR block in one availability zone. A public subnet is public because its route table sends 0.0.0.0/0 to an internet gateway. AWS reserves five addresses in every subnet, so a /24 gives you 251 usable addresses, not 256.

**Route tables**  
Each subnet follows exactly one route table. The local route for the VPC CIDR cannot be deleted. For everything else, the longest prefix match picks the next hop, so a /32 route can override the default.

**Internet and NAT**  
An internet gateway attaches to the VPC and gives public subnets a path in and out. A NAT gateway gives private subnets outbound access only: it translates their addresses to its own public IP and drops unsolicited inbound traffic. It sits in a public subnet and holds an elastic IP.

**Security groups and NACLs**  
Security groups are stateful and allow-only: the reply to an allowed connection is allowed automatically. NACLs are stateless and evaluated in numbered order, first match wins, so both directions need a rule. A group attaches to an elastic network interface; a NACL attaches to a subnet.

> **The honest caveat:** most VPC outages are a rule in the wrong place, such as a NACL deny or a private route table with no NAT route.

> **The lesson:** read the four together, because a correct rule in the wrong layer still drops the packet.

## In one line

> **Four layers, one packet path.** A correct rule in the wrong layer still drops the packet.

**Trace the route**

```bash
aws ec2 describe-route-tables
```
