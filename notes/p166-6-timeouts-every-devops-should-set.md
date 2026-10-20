---
id: p166
title: "6 timeouts every DevOps should set"
slug: 6-timeouts-every-devops-should-set
sections: [devsecops]
topic: "Observability & SRE"
tags: [DevOps, SRE, Reliability, CloudComputing, SysAdmin]
source: "LinkedIn post P166 · IT series"
linkedin_date: 2027-10-19
design: numbers
---

# 6 timeouts every DevOps should set

The default timeout for most things is either far too long or infinite. A single call with no timeout can tie up a worker forever, and enough of them take the whole service down. Six timeouts worth setting on purpose.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **5 s** | TCP connect | Fail fast when a host is unreachable, not after a minute. | connect |
| **30 s** | HTTP client | Cap how long a call to another service can hang. | request |
| **10 s** | Liveness probe | How long before the platform restarts a stuck pod. | k8s |
| **30 s** | Graceful shutdown | Time to finish in-flight work before a hard kill. | SIGTERM |
| **60 s** | Load balancer idle | Must exceed your app's keep-alive, or you get resets. | LB |
| **30 s** | DB statement | Kill a runaway query before it blocks everything. | query |

## Explained

5 s, TCP connect. How long to wait to establish a connection before giving up. If a host is down or a firewall is dropping packets, you want to fail in seconds, not after the operating system's default minute or more.

30 s, HTTP client. The total time a call to another service or API may take. Without it, one slow dependency makes your app hang too, and the hang spreads upstream. This is the classic cause of cascading failures.

10 s, liveness probe. In Kubernetes, how long a pod can be unresponsive before it is restarted. Too short and healthy-but-busy pods get killed; too long and users suffer before recovery.

30 s, graceful shutdown. The time a process gets to finish in-flight requests after a stop signal before it is force-killed. Too short and you drop requests on every deploy.

60 s, load balancer idle. The idle timeout on the load balancer should be longer than your app's keep-alive timeout. If the app closes connections first, users get confusing resets.

30 s, database statement. A statement timeout kills a runaway query before it holds locks and blocks every other connection.

> **The rule behind all of them:** every network call needs a timeout. A call that can wait forever will, eventually, on the worst possible day.

## In one line

> **A missing timeout is an outage waiting.** Defaults are often minutes, or infinite. Set them on purpose.

**The rule:** every network call needs a timeout
