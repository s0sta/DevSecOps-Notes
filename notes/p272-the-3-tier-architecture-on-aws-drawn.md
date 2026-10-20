---
id: p272
title: "The 3-tier architecture on AWS, drawn"
slug: the-3-tier-architecture-on-aws-drawn
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, CloudArchitecture, DevOps, CloudNative, SystemDesign]
source: "LinkedIn post P272 · Visual series"
linkedin_date: 2028-06-22
design: architecture
---

# The 3-tier architecture on AWS, drawn

Most AWS bills and outages start with a diagram nobody drew. The classic web app still has three tiers, and every request walks the same path through them.

## Quick reference

- **Tier 1 · Edge:** Route 53 (DNS) · CloudFront (CDN) · AWS WAF (WAF)
- **Tier 2 · Application:** Load balancer (ALB) · EC2 auto scaling (APP) · IAM role (IAM)
- **Tier 3 · Data:** Aurora (DB) · ElastiCache (CACHE) · S3 objects (OBJ)

**Request flow:** Route 53 → CloudFront → AWS WAF → Load balancer → EC2 auto scaling → Aurora; EC2 auto scaling → ElastiCache; EC2 auto scaling → S3 objects

**Around it:** CloudWatch (LOG) · CloudTrail (AUDIT) · KMS (KEYS) · Backup (BCK)

## Explained

Edge. Route 53 answers DNS, CloudFront caches at the edge, and AWS WAF filters the request before it reaches your account. The edge tier exists to absorb traffic you never want to see again.

Application. An Application Load Balancer spreads connections across EC2 instances in an auto scaling group. The group adds capacity when CPU climbs and removes it when traffic drops. An IAM role gives the instances permission to call other services without a stored key.

Data. Aurora holds the transactional data, ElastiCache takes the hot reads, and S3 stores media and documents. Each tier fails differently: edge failures are DNS or certificate problems, application failures are capacity or code, data failures are locks and disk.

Around the three tiers sit the services that keep them honest: CloudWatch for metrics and alarms, CloudTrail for the audit trail, KMS for encryption keys, Backup for recovery, and a load balancer that only sends traffic to instances that pass their health check.

> **The lesson:** the value of the diagram is the arrows. A box tells you what you bought; an arrow tells you what breaks when it dies.

## In one line

> **Draw it before you build it.** A diagram is the cheapest design review you will ever run.

**Trace one request**

```bash
curl -sv https://example.com
```
