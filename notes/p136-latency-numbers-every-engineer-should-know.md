---
id: p136
title: "Latency numbers every engineer should know"
slug: latency-numbers-every-engineer-should-know
sections: [devsecops]
topic: "DevOps basics"
tags: [SoftwareEngineering, Performance, SystemDesign, DevOps, CloudComputing]
source: "LinkedIn post P136 · IT series"
linkedin_date: 2027-08-10
design: numbers
---

# Latency numbers every engineer should know

You do not need to memorise exact nanoseconds. You need the orders of magnitude, because they explain nearly every performance decision you will make. These are the classic "latency numbers every engineer should know", rounded for memory.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **1 ns** | L1 cache | The CPU's fastest memory. The baseline for everything. | ~ |
| **100 ns** | Main memory (RAM) | About 100x slower than L1. Still very fast. | RAM |
| **16 us** | SSD read | Solid-state storage. Microseconds, not milliseconds. | NVMe |
| **2 ms** | Disk seek (HDD) | A spinning disk. Thousands of times slower than RAM. | HDD |
| **0.5 ms** | Same datacenter | A network round trip between nearby servers. | LAN |
| **150 ms** | Across the world | A round trip between continents. Physics, not your code. | WAN |

## Explained

1 ns, L1 cache. The CPU's fastest memory, right next to the core. Everything else is measured against this.

100 ns, main memory. Reading from RAM is roughly 100 times slower than L1 cache. Still astonishingly fast, which is why keeping data in memory beats fetching it again.

16 us, an SSD read. Microseconds. Modern NVMe drives are thousands of times faster than spinning disks, which is why moving a database onto SSD can feel like a different machine.

2 ms, a disk seek on a spinning HDD. The mechanical arm has to move. This is why random reads on HDDs are slow and sequential reads are fine.

0.5 ms, a round trip inside the same datacenter. Local network calls are cheap, but not free. A thousand of them in a loop still adds up.

150 ms, a round trip between continents. This is the speed of light over distance, not slow code. No optimisation removes it. You hide it by putting data and servers closer to users, with CDNs and regions.

> **The lesson behind the numbers:** reach for cache before RAM, RAM before disk, and local before remote. Most performance work is just moving data up this ladder.

## In one line

> **Know the orders of magnitude.** They explain why caching and location matter so much.

**Measure one**

```bash
ping -c 4 your-server
```
