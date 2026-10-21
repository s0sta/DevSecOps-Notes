---
id: p499
title: "The life of a NAT connection"
slug: the-life-of-a-nat-connection
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, NATGateway, Networking, VPC, CloudComputing]
source: "LinkedIn post P499 · Network series"
linkedin_date: 2029-12-04
design: timeline
---

# The life of a NAT connection

A NAT connection is a mapping with a clock on it. The instance sees a normal TCP session; the gateway sees a port, a timer and a table.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **0 ms** | Outbound SYN | The instance sends a SYN; its default route points at the NAT gateway. |
| **1 ms** | Source NAT | The gateway rewrites the source to its own address and a free port. |
| **2 ms** | Connection tracked | The five-tuple mapping is stored so returning packets can be matched. |
| **40 ms** | The reply | The server answers the Elastic IP; the gateway maps it back. |
| **350 s** | Idle timeout | Idle for 350 seconds, the mapping is removed; a late packet gets an RST. |
| **351 s** | Port reuse | The port returns to the pool and the next connection can take it. |

## Explained

### The first milliseconds

0 ms. The instance sends a SYN to a public address. Its default route points at the NAT gateway, so the packet goes there.

1 ms. The gateway rewrites the source to its own private address and a free port; the internet gateway maps that to the Elastic IP. That is source NAT, and the port is the scarce resource: 55,000 connections per unique destination per address.

2 ms. It stores the five-tuple mapping, so it can recognise the reply. The connection is now state on the gateway, not just on the instance.

### The rest of its life

40 ms. The server replies to the Elastic IP and the mapped port. The gateway translates it back and the instance never knows.

350 s. If no packet crosses the mapping for 350 seconds, the idle timer removes it. If the instance keeps sending, it gets an RST, not a FIN.

351 s. The port returns to the pool, and the next connection can reuse it.

> **The honest caveat:** 350 seconds is the idle timeout, not a maximum lifetime. A keepalive under 350 seconds holds the mapping open, and a client that opens connections faster than they close can exhaust the ports.

> **The lesson:** a NAT gateway is stateful, and every state has a timer.

## In one line

> **The mapping is the connection.** A NAT gateway remembers state so your instance does not have to.

**Watch the idle count:** IdleTimeoutCount
