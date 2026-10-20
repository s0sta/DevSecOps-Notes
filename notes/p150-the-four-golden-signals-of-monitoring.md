---
id: p150
title: "The four golden signals of monitoring"
slug: the-four-golden-signals-of-monitoring
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, Monitoring, Observability, DevOps, CloudComputing]
source: "LinkedIn post P150 · IT series"
linkedin_date: 2027-09-12
design: dashboard
---

# The four golden signals of monitoring

Google's SRE book boils monitoring down to four golden signals. If you can only watch a few things on a service, watch these, because together they tell you whether users are having a good time.

## Quick reference

**Status:** What good monitoring measures

| Metric | Value | Note |
|:--|:--|:--|
| LATENCY | **182 ms** | p95 response time. How slow? |
| TRAFFIC | **1.2k/s** | requests per second. How much? |
| ERRORS | **0.4%%** | share of failed requests |
| SATURATION | **68%** | how full the system is |
| Watch together | **4** | one hides, four reveal |
| Alert on | **SLO** | symptoms users feel |

## Explained

Latency: how long requests take. Measure it at a percentile, like p95 or p99, not an average, because averages hide the slow tail that real users feel. And separate successful from failed requests, since a fast error is still an error.

Traffic: how much demand the system is under, such as requests per second. On its own it is just a number, but next to the others it gives meaning. A spike in latency during a traffic spike is capacity; a spike in latency with flat traffic is a problem.

Errors: the rate of failed requests, as a share of the total. This is the most direct signal that something is broken. Watch both obvious failures, like HTTP 500s, and silent ones, like wrong responses with a 200 status.

Saturation: how full the system is, the resource closest to its limit, whether that is CPU, memory, disk or a connection pool. Saturation is a leading indicator: it climbs before latency and errors do, giving you warning.

Why four and not forty: a wall of CPU and memory graphs tells you how the machine feels. These four tell you how the user feels, and that is what an alert should be about.

The practical rule: alert on symptoms users notice, like latency and errors against your SLO, and use saturation to see trouble coming.

## In one line

> **Measure what users feel.** CPU graphs are nice. These four tell you if users are happy.

**The four:** latency, traffic, errors, saturation
