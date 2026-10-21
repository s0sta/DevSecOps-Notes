---
id: p492
title: "VPC routing, drawn"
slug: vpc-routing-drawn
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, VPC, Networking, CloudComputing, DevOps]
source: "LinkedIn post P492 · Network series"
linkedin_date: 2029-11-18
design: architecture
---

# VPC routing, drawn

A subnet is not public because of a checkbox. It is public because one route in its route table points at an internet gateway.

## Quick reference

- **Subnets:** Public subnet (PUB) · Private subnet (PRIV)
- **Route table:** Local route (LOCAL) · Default route (0/0)
- **Gateways:** Internet gateway (IGW) · NAT gateway (NAT)

**Request flow:** Public subnet → Local route; Private subnet → Local route; Default route → Internet gateway; Default route → NAT gateway → Internet gateway

## Explained

### Subnets

Public subnet, private subnet: both are CIDR ranges tied to one Availability Zone. The difference is which route table is associated with them. A subnet with the public table can reach the internet gateway directly. A subnet with the private table cannot.

### Route table

Every route table starts with a local route: 10.0.0.0/16 to local. AWS creates it, it cannot be deleted, and it keeps traffic for the VPC inside the VPC. The route that decides egress is the default route, 0.0.0.0/0. Point it at the internet gateway and the subnet is public. Point it at a NAT gateway and the subnet is private with outbound access. Longest prefix wins, so the local route always beats the default for VPC addresses.

### Gateways

The internet gateway is attached to the VPC, not to a subnet. It is horizontally scaled and performs one-to-one NAT for instances with a public IPv4 address. The NAT gateway is different: it sits in a public subnet, holds an Elastic IP, and maps many private sources to its own address. It only passes connections initiated from inside.

> **The honest caveat:** a zonal NAT gateway is per Availability Zone. Put one NAT in one zone and every other zone now crosses an AZ boundary, pays cross-AZ transfer and shares the failure.

> **The lesson:** the route table is the policy. The gateways are just where the packets go.

## In one line

> **The route table is the network.** Public is a route, not a checkbox.

**Trace the route**

```bash
aws ec2 describe-route-tables
```
