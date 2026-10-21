---
id: p498
title: "Anatomy of a route table entry"
slug: anatomy-of-a-route-table-entry
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, VPC, Networking, Routing, CloudComputing]
source: "LinkedIn post P498 · Network series"
linkedin_date: 2029-12-02
design: anatomy
---

# Anatomy of a route table entry

Most routing incidents are one line long. The route table is where the intent is written down, and one entry carries the whole story.

## Quick reference

```text
10.0.0.0/16 -> local (active) [vpc]
```

| Part | Name | What it means |
|:--|:--|:--|
| `10.0.0.0/16` | Destination | The prefix to match. Longest match wins, so a /24 beats a /16. |
| `->` | The arrow | Read it as: send this prefix to the target on the right. |
| `local` | Target | The VPC itself. Created by AWS, and it cannot be deleted. |
| `(active)` | State | The target exists. Blackhole means it was deleted and the route stayed. |
| `[vpc]` | Scope and origin | This entry belongs to this VPC's table and applies only to associated subnets. |

## Explained

### Destination and arrow

10.0.0.0/16 is the destination: the prefix this entry matches. The router compares every route and picks the longest match, so a /24 beats a /16. A /16 is a broad promise; a /24 is a narrow one, and the narrow one wins. The arrow is not decoration; it says send this prefix to the target on the right.

### Target and state

local is the target. It means the VPC itself, the route AWS creates in every table, and the one you cannot delete. (active) is the state: the target exists and the route can forward. If the target is deleted, the state becomes blackhole and the same line silently drops traffic.

### Scope and origin

[vpc] is the scope, the part the CLI does not print as a token. The entry belongs to this VPC and this table only, and the table applies only to the subnets associated with it. Every other subnet is reading a different list. Change the association and every subnet that reads this list changes with it.

> **The honest caveat:** a correct route proves intent, not delivery. A security group, a NACL or a target that refuses the packet can still drop it after the route matched.

> **The lesson:** read the line before you redraw the diagram.

## In one line

> **A route is a promise.** The table records intent; the packet still has to survive the path.

**Read a table**

```bash
aws ec2 describe-route-tables
```
