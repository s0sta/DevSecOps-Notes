---
id: p501
title: "5 VPC mistakes"
slug: 5-vpc-mistakes
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, VPC, CloudSecurity, Networking, DevOps]
source: "LinkedIn post P501 · Network series"
linkedin_date: 2029-12-09
design: dontdo
---

# 5 VPC mistakes

Most VPC incidents are decisions made on day one, when the diagram was simple and the deadline was real.

## Quick reference

**1.** ❌ **Overlapping CIDRs across VPCs** — Peering and Transit Gateway cannot route between them; re-IP later hurts.  
✅ **Plan a global CIDR scheme** — One range per VPC, no overlap, documented before build.

**2.** ❌ **0.0.0.0/0 on SSH and RDP** — The whole internet can reach the admin port; scanners find it in hours.  
✅ **SSM Session Manager, no port** — No inbound rule, no bastion, and every session is logged.

**3.** ❌ **Private subnet with no egress** — No NAT or endpoints: package installs and updates fail at 3 a.m.  
✅ **NAT per AZ or VPC endpoints** — Egress works, and endpoints keep AWS traffic off the NAT.

**4.** ❌ **One subnet, one AZ** — An AZ outage takes the service down; the SLA does not cover it.  
✅ **Two AZs, one subnet each** — Failover is a routing change, not a rebuild.

**5.** ❌ **No flow logs, no evidence** — You cannot prove who talked to what, or why a packet died.  
✅ **Flow logs to S3 or CloudWatch** — Cheap evidence, and the first place to look after a drop.

## Explained

### The five

1. **Overlapping CIDRs.** Two VPCs both on 10.0.0.0/16 can never peer. Re-IP later means touching every subnet, route and firewall rule; plan a global range before the second VPC exists.

2. 0.0.0.0/0 on admin ports. SSH and RDP open to the world are found by scanners in hours. Use SSM Session Manager, or a bastion with a security group that names the source.

3. **No egress path.** A private subnet with no NAT gateway, no VPC endpoints and no other route out cannot install a package or reach an API. The failure appears at the worst moment, not at build time.

4. **One AZ.** One subnet in one Availability Zone is one power domain, one NAT gateway and one failure. Two subnets in two zones turn an outage into a routing change.

5. **No flow logs.** Without them, a dropped packet is an opinion. Flow logs to S3 or CloudWatch are cheap evidence, and the first place to look.

### The pattern

Each one trades a small convenience today for a larger failure later.

> **The honest caveat:** none of these is a security control on its own. They are the defaults that let the other controls do their job.

> **The lesson:** the network you draw on day one is the one you debug at 3 a.m.

## In one line

> **Design the network for the bad day.** The bill for a shortcut arrives with interest.

**Check the cidrs**

```bash
aws ec2 describe-vpcs
```
