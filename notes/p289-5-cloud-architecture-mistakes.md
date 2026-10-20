---
id: p289
title: "5 cloud architecture mistakes"
slug: 5-cloud-architecture-mistakes
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, CloudArchitecture, DevOps, CloudSecurity, SRE]
source: "LinkedIn post P289 · Visual series"
linkedin_date: 2028-08-01
design: dontdo
---

# 5 cloud architecture mistakes

None of these decisions looks wrong on the day it is made. Each one saves a little time or money, and sends the bill to the person on call.

## Quick reference

**1.** ❌ **Everything in one subnet** — One route table means nothing is private.  
✅ **Split public and private** — Each subnet gets only the route it needs.

**2.** ❌ **A single availability zone** — One zone outage takes the whole app down.  
✅ **Two zones from day one** — A zone failure becomes a failover, not an outage.

**3.** ❌ **Long-lived access keys** — A leaked key outlives the person who made it.  
✅ **Roles and OIDC federation** — Credentials expire in minutes, not years.

**4.** ❌ **No tags, no budgets** — The bill arrives with no way to split it.  
✅ **Owner and cost tags** — Every resource names who pays for it.

**5.** ❌ **Backups never tested** — An untested backup is a hope, not a plan.  
✅ **A restore drill each quarter** — You learn the restore time before an incident.

## Explained

### The five

1. **Everything in one subnet.** One subnet means one route table, and a route that reaches the internet makes the subnet public. Split public from private and route the private side through a NAT gateway.

2. **A single availability zone.** One zone outage takes the whole app with it. Two zones turn that outage into a failover; cross-zone traffic costs a little, downtime costs more.

3. **Long-lived access keys.** A key in a CI variable outlives the person who made it. Roles and OIDC federation give workloads credentials that expire in minutes.

4. **No tags, no budgets.** The bill arrives with no way to split it and nobody can name the team behind the expensive queue. Owner and cost-centre tags cost nothing now and hurt to retrofit.

5. **Backups never tested.** An untested backup is a hope. A quarterly restore drill gives you the restore time before an incident needs it, and proves the backup exists.

### What they share

Each one is a shortcut in the architecture, not in the code, which is why a code review never catches it.

> **The honest caveat:** two zones and a tested restore still do not cover a bad deploy or a deleted table; for that you need versioning, point-in-time recovery and a rollback you have practised.

> **The lesson:** the cheapest architecture decision is the one you review before you build.

## In one line

> **Small shortcuts, large outages.** The bill and the incident both start with the same decision.

**Check your subnets**

```bash
aws ec2 describe-subnets
```
