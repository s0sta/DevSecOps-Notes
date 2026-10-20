---
id: p291
title: "Quiz: 3 cloud architecture questions"
slug: quiz-3-cloud-architecture-questions
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, CloudArchitecture, CloudSecurity, DevOps, CloudNative]
source: "LinkedIn post P291 · Visual series"
linkedin_date: 2028-08-06
design: quiz
---

# Quiz: 3 cloud architecture questions

Three questions separate an architecture you can explain from one you have only copied. Answer before the reveal.

## Quick reference

**Q1. Why fix availability across two AZs before adding a region?**

- a) AZ failure is common; region failure is rare
- b) A second region is cheaper than a second AZ
- c) Multi-region removes the need for backups

> **Answer:** a) AZ failure is common; region failure is rare. AZs are separate data centres in one region. An AZ failure is realistic, a region failure is rare, and multi-region costs far more in money and complexity.

**Q2. What does a NAT gateway actually do?**

- a) Gives private subnets outbound access only
- b) Publishes private addresses to the internet
- c) Removes the need for a route table

> **Answer:** a) Gives private subnets outbound access only. It translates private addresses to its own public IP for outbound traffic and drops unsolicited inbound. It belongs in a public subnet with a private route.

**Q3. Why is the shared responsibility model split at all?**

- a) No single party can secure every layer
- b) AWS owns the data, the customer owns the metal
- c) Compliance requires exactly one owner

> **Answer:** a) No single party can secure every layer. The provider secures facilities, hardware and the platform; the customer owns data, access and configuration. Gaps appear where each side assumes the other.

## Explained

**The zone and the region**  
Question one: why two availability zones before a second region? Because an AZ is a data centre and a region is a group of them. Zone failures happen, region failures are rare, and two zones buy the common failure for the cost of duplicated capacity. A second region buys the rare one for far more money, data transfer and operational work.

**The middle box**  
Question two: what does a NAT gateway do? It lets a private subnet start outbound connections by translating their addresses to the gateway's public IP, and it drops unsolicited inbound. It is not a reverse proxy and it does not make a private subnet public. It sits in a public subnet and needs a route from the private one.

**The moving line**  
Question three: why is shared responsibility split? Because no single party can secure every layer. AWS owns the buildings, hardware and managed platform; you own the data, the identities and the configuration. The split moves with the service, which is why the same control can be yours on EC2 and AWS's on Lambda.

> **The honest caveat:** the model is a map, not an audit. A shared control such as patching needs a named owner on your side, or both teams will assume the other one has it.

> **The lesson:** know where your responsibility starts, and write it down.

## In one line

> **Know where your responsibility starts.** Three answers that decide what you own.

**Audit your side**

```bash
aws iam generate-credential-report
```
