---
id: p286
title: "Multi-region active-active, drawn"
slug: multi-region-active-active-drawn
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, CloudArchitecture, SRE, DevOps, CloudNative]
source: "LinkedIn post P286 · Visual series"
linkedin_date: 2028-07-25
design: architecture
---

# Multi-region active-active, drawn

Active-active is easy to draw and hard to finish. The application tier multiplies cleanly; the database is where the diagram starts lying.

## Quick reference

- **Tier 1 · Edge:** Route 53 latency (DNS) · Health checks (HC)
- **Tier 2 · Region a:** ALB (ALB) · App servers (APP) · Aurora writer (DB)
- **Tier 3 · Region b:** ALB (ALB) · App servers (APP) · Aurora replica (DB)

**Request flow:** Health checks → Route 53 latency → ALB → App servers → Aurora writer → Aurora replica; Route 53 latency → ALB → App servers → Aurora replica

## Explained

**Edge**  
Route 53 holds latency records for both regions, so each user is answered by the region with the lowest measured latency. Latency is measured per resolver, so a user in Riyadh and a user in Dublin can land in different regions. Health checks watch each regional endpoint, and when one fails, Route 53 stops returning it. That is the whole failover for reads and for stateless requests.

**Region A and Region B**  
Each region has its own load balancer, its own application servers and its own Aurora endpoint. The load balancers are regional, the application servers hold no session state, and either region can serve a request without asking the other. Reads are served locally in both.

**The database**  
Aurora Global Database keeps a read replica in Region B. Replication is asynchronous, typically under a second, and the replica stays read-only while the writer in Region A lives. Promotion of the secondary takes about a minute and can lose the last few transactions, so plan for a small window of lost writes.

> **The honest caveat:** this design is active-active for reads and active-passive for writes. Calling it active-active without saying that is how teams discover the difference during a failover.

> **The lesson:** availability is a property of each tier, not of the diagram.

## In one line

> **Active-active is a per-tier claim.** The application can be active in both regions; the writer cannot.

**Check the lag**

```bash
aws rds describe-global-clusters
```
