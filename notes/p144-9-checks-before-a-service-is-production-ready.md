---
id: p144
title: "9 checks before a service is production-ready"
slug: 9-checks-before-a-service-is-production-ready
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, SRE, CloudNative, Kubernetes, BestPractices]
source: "LinkedIn post P144 · IT series"
linkedin_date: 2027-08-29
design: checklist
---

# 9 checks before a service is production-ready

"It works on my machine" and "it is ready for production" are far apart. Nine checks that close the gap, whether you deploy to Kubernetes, a VM or a platform.

## Quick reference

### It runs well

- **Health endpoint** — liveness and readiness
- **Config from env** — no secrets in the image
- **Resource limits set** — CPU and memory requests

### It survives

- **Restarts cleanly** — stateless, or state elsewhere
- **Graceful shutdown** — finishes in-flight requests
- **Two or more replicas** — no single point of failure

### You can see it

- **Structured logs** — to stdout, with levels
- **Metrics exposed** — /metrics or an agent
- **Alerts wired up** — to a person, not a void

## Explained

### It runs well

Health endpoint. A liveness check so the platform can restart a hung process, and a readiness check so traffic only arrives once the app can actually serve it.  
Config from the environment. Settings and secrets come from environment variables or a secrets manager, never baked into the image. The same image then runs in staging and production unchanged.  
Resource limits set. CPU and memory requests and limits, so the scheduler can place it and one hungry service cannot starve the rest.

### It survives

Restarts cleanly. The app can be killed and restarted at any moment with no data loss. State lives in a database or cache, not on the local disk.  
Graceful shutdown. On a stop signal it finishes in-flight requests and closes connections, instead of dropping users mid-request.  
Two or more replicas. One instance is a single point of failure. Two or more, spread across nodes, survive a crash or a node dying.

### You can see it

Structured logs to stdout, with log levels, so the platform collects them and you can search them.  
Metrics exposed, through a /metrics endpoint or an agent, so you can see request rate, errors and latency.  
Alerts wired to a person. An alert that reaches a dashboard nobody watches is not monitoring.

The fastest honesty test: kill the instance in staging and watch whether it recovers on its own.

## In one line

> **Works on my machine is not ready.** Production-ready means it survives and tells you how it is.

**The quick test:** kill the pod and watch it recover
