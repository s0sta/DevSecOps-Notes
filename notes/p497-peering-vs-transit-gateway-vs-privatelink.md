---
id: p497
title: "Peering vs Transit Gateway vs PrivateLink"
slug: peering-vs-transit-gateway-vs-privatelink
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, Networking, TransitGateway, PrivateLink, CloudArchitecture]
source: "LinkedIn post P497 · Network series"
linkedin_date: 2029-11-29
design: matrix
---

# Peering vs Transit Gateway vs PrivateLink

Three ways to connect VPCs, and the invoice explains the difference before the diagram does.

## Quick reference

| | **Peering** | **Transit Gateway** | **PrivateLink** |
|:--|:--|:--|:--|
| Model | VPC to VPC, one to one | Regional hub and spoke | Service to consumer |
| Scale | 50 peers, 125 on request | 5,000 attachments | Endpoint ENIs per subnet |
| Routing | Routes on both sides | Transitive, route tables | No routes, DNS endpoint |
| Security | SG refs, same Region | Central inspection VPC | One-way, no CIDR overlap |
| Cost | Per GB only | Attachment-hour + GB | Endpoint-hour + GB |
| Best for | A few VPCs, low latency | Many VPCs, shared egress | SaaS and shared services |

**How to pick**

- **Peering** → two VPCs, two route tables, no transit.
- **TGW** → one hub, many attachments, one route table.
- **PrivateLink** → one service, one endpoint, no route.

## Explained

### Peering

One-to-one, two route tables, no transit. Each side adds a route for the other VPC, and neither can pass traffic to a third. Overlapping CIDRs are refused outright. The default is 50 active peers per VPC, adjustable to 125. You pay for data transfer, not for the connection. In the same Region, a security group can reference the peer's group. Peering is the simplest option only while the mesh is small.

### Transit Gateway

A regional hub. Attach VPCs, VPNs and Direct Connect gateways, and let the route tables decide what talks. It routes transitively, so a spoke reaches another spoke through the hub, and central egress or inspection becomes one attachment. The default is 5,000 attachments, and you pay per attachment-hour plus data.

### PrivateLink

Not a network path: a service endpoint. The consumer creates an interface endpoint in its own subnet, DNS resolves the service name to it, and traffic stays on the AWS network. The provider cannot initiate back. No route table entry, and overlapping CIDRs are not a problem, which is why it works between tenants that could never peer. You pay per endpoint-hour plus data.

> **The honest caveat:** PrivateLink gives you a service, not a route. If you need the provider to initiate, or a full network path, it is the wrong tool.

> **The lesson:** choose the shape of the relationship, then choose the product.

## In one line

> **Pick the shape before the bill.** The cheapest connection is the one that matches the shape of your estate.

**Count the attachments**

```bash
aws ec2 describe-transit-gateways
```
