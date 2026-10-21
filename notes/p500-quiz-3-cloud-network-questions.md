---
id: p500
title: "Quiz: 3 cloud network questions"
slug: quiz-3-cloud-network-questions
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, VPC, Networking, CloudSecurity, DevOps]
source: "LinkedIn post P500 · Network series"
linkedin_date: 2029-12-06
design: quiz
---

# Quiz: 3 cloud network questions

Three questions that separate a VPC diagram from a VPC that works. Answer before the reveal.

## Quick reference

**Q1. Why can two VPCs with overlapping CIDRs not be peered?**

- a) The route table cannot tell them apart
- b) The peering limit is one per account
- c) AWS blocks all RFC 1918 ranges

> **Answer:** a) The route table cannot tell them apart. A route matches on prefix. If both VPCs own 10.0.0.0/16, a packet to 10.0.0.7 has two homes, so AWS refuses the peering connection outright.

**Q2. What does a NAT gateway not allow?**

- a) Inbound connections from the internet
- b) Outbound connections to the internet
- c) Return traffic for an outbound request

> **Answer:** a) Inbound connections from the internet. It maps outbound connections and their replies. An unsolicited inbound SYN has no mapping, so it is dropped; publish the service behind a load balancer instead.

**Q3. Why does a network ACL need a rule for the reply?**

- a) Because it is stateless
- b) Because security groups drop replies
- c) Because routes rewrite the source port

> **Answer:** a) Because it is stateless. A security group remembers the connection and allows the reply. A NACL checks each direction alone, so the reply needs its own rule, usually ports 1024-65535.

## Explained

### Question one

Why can two VPCs with overlapping CIDRs not be peered? Because a route matches on prefix. If both VPCs own 10.0.0.0/16, a packet to 10.0.0.7 has two possible homes, and no route table can choose. AWS refuses the peering connection outright, so the fix is to re-IP before you need the link, not after. The limit is not a policy choice; it is arithmetic.

### Question two

What does a NAT gateway not allow? Inbound connections initiated from the internet. It maps outbound connections and their replies; an unsolicited SYN has no mapping and is dropped. A NAT gateway is stateful for the connections it opened, and nothing else. Publish the service behind a load balancer if it must accept connections.

### Question three

Why does a NACL need a rule for the reply? Because it is stateless. A security group remembers the connection and allows the return traffic; a NACL checks each direction alone, so the reply needs its own rule, usually an ephemeral port range of 1024-65535.

> **The honest caveat:** these are the common answers, not every answer. A NAT instance, a firewall appliance or a PrivateLink endpoint changes the path, and the rules change with it.

> **The lesson:** state is the difference between a rule and a session.

## In one line

> **One hop remembers, one does not.** State is the difference between a rule and a session.

**Read the counters**

```bash
aws ec2 describe-network-acls
```
