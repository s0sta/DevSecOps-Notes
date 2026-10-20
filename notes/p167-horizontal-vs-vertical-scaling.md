---
id: p167
title: "Horizontal vs Vertical scaling"
slug: horizontal-vs-vertical-scaling
sections: [devsecops]
topic: "DevOps basics"
tags: [CloudComputing, SystemDesign, DevOps, Scalability, SRE]
source: "LinkedIn post P167 · IT series"
linkedin_date: 2027-10-21
design: compare
---

# Horizontal vs Vertical scaling

When a system is overloaded, there are two ways to give it more capacity: make the machine bigger, or add more machines. Each fits a different problem.

## Quick reference

| | **VERTICAL** | **HORIZONTAL** |
|:--|:--|:--|
| How | Upgrade the machine | Add more machines |
| Limit | The biggest box | Almost none |
| Downtime | Often a reboot | None, add live |
| Redundancy | Still one machine | Survives one failing |
| Needs | Simple | Load balancer, stateless app |
| Best for | Databases, quick wins | Web and app tiers |

**VERTICAL** (A bigger box): Give the existing server more CPU, memory or disk.

Example: `2 vCPU -> 8 vCPU`

**HORIZONTAL** (More boxes): Add more servers and spread the load across them.

Example: `1 server -> 5 servers`

- Vertical → fast and simple, until you hit the ceiling.
- Horizontal → scales far and survives failures. Design for it.

## Explained

Vertical scaling means giving the existing server more resources: more CPU, more memory, a faster disk. 2 vCPUs become 8. It is the simplest option, needs no change to your application, and is often the fastest fix. The limits are real, though. There is a biggest box you can buy, it is still a single point of failure, and resizing usually means a reboot and a moment of downtime.

Horizontal scaling means adding more servers and spreading the load across them with a load balancer. One app server becomes five. There is almost no ceiling, you can add or remove capacity while the system is live, and if one server dies the others carry on. The cost is design: your app must be stateless, or keep its state in a shared database or cache, so any server can handle any request.

### How to choose

Vertical: a database, or a quick win under sudden load. Simple, but temporary.  
Horizontal: web and application tiers, where you need to scale far and survive failures. The cloud-native default.

A common pattern combines them: scale the stateless web and app tiers horizontally behind a load balancer, and scale the database vertically, because databases are harder to spread across machines.

The deeper point: horizontal scaling is as much an application design decision as an infrastructure one. Build stateless, and scaling out becomes easy later.

Vertical is fast. Horizontal goes far.
