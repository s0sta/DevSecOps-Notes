---
id: p200
title: "The DORA metrics: 4 numbers that measure delivery"
slug: the-dora-metrics-4-numbers-that-measure-delivery
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, DORA, SRE, CICD, EngineeringMetrics]
source: "LinkedIn post P200 · Cloud / DevSecOps series"
linkedin_date: 2028-01-06
design: numbers
---

# The DORA metrics: 4 numbers that measure delivery

How do you know if your delivery is actually good? The DORA research, from years of State of DevOps reports, boils it down to four metrics. Two measure speed, two measure stability, and the big finding is that the best teams score well on all four at once.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **Deploy freq** | How often you ship | Elite teams deploy on demand, many times a day. | speed |
| **Lead time** | Commit to production | Elite: under an hour. Low: over a month. | speed |
| **Change fail %** | Deploys that break | Elite: 0-15%. The quality side of speed. | quality |
| **MTTR** | Time to recover | Elite: under an hour. How fast you bounce back. | quality |
| **2** | Speed vs stability | The myth is you trade them. The data says you don't. | insight |
| **DORA** | The research | From the State of DevOps reports. The industry standard. | source |

## Explained

Deployment frequency: how often you release to production. Elite teams deploy on demand, many times a day; lower performers release weekly or monthly. Frequent, small deploys are safer than rare, big ones.

Lead time for changes: how long from a commit to that code running in production. Elite teams measure this in under an hour; the slowest in weeks or months. It reflects how much friction sits between an idea and users.

Change failure rate: the share of deploys that cause a problem needing a fix or rollback. Elite teams keep it in the 0 to 15% range. This is the quality counterweight to deploy frequency.

Mean time to recovery (MTTR): when something does break, how fast you restore service. Elite teams recover in under an hour. Fast recovery matters more than never failing, because everything fails eventually.

The insight that changed the industry: speed and stability are not a trade-off. The data shows the same teams that deploy most often also fail least and recover fastest, because small, frequent, automated changes are easier to test, ship and reverse.

Where to start: you do not need a fancy tool. Begin by tracking deployment frequency and MTTR, and the conversations they start will improve the rest.

## In one line

> **Speed and stability rise together.** Good teams ship more often AND break less. Measure both.

**Start measuring:** track deploy frequency and MTTR first
