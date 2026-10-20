---
id: p242
title: "Platform engineering terms, decoded"
slug: platform-engineering-terms-decoded
sections: [devsecops]
topic: "Platform engineering"
tags: [PlatformEngineering, DevOps, Kubernetes, SRE, CloudNative]
source: "LinkedIn post P242 · Platform series"
linkedin_date: 2028-04-13
design: reveal
---

# Platform engineering terms, decoded

Platform engineering is the rename of the year: the same infrastructure work, now with users who can say no. The vocabulary is where most conversations go wrong.

## Quick reference

- **IDP** — Internal Developer Platform: the self-service layer over Kubernetes and cloud, so developers touch neither.
- **Golden path** — The supported route for a new service: template, CI, deploy, dashboards and alerts, already wired.
- **Service catalog** — The index of every service, its owner, repo and dependencies. Backstage is the usual home for it.
- **Scorecard** — An automatic per-service checklist: tests, SLO, runbook, owner. It shows gaps, not grades.
- **Tenant** — One team's slice of the platform: namespace, quota, RBAC and cost, fenced off from the others.
- **Self-service** — A team creates what it needs through a form or a pull request, without a ticket to the platform team.

## Explained

### The layer

An IDP, Internal Developer Platform, is the self-service layer a platform team runs over Kubernetes and cloud. Its job is to keep developers out of both.  
A golden path is the supported route for a new service: template, CI, deploy, dashboards and alerts, already wired. A default, not a mandate: teams can leave it, but they pay the support cost.  
A service catalog is the index of every service, its owner, repo and dependencies. Backstage is the usual home for it.  
A scorecard checks each service against tests, SLO, runbook and owner, automatically. It shows gaps, not grades.  
A tenant is one team's slice of the platform: namespace, quota, RBAC and cost, fenced off from the others.  
Self-service means a team creates what it needs through a form or a pull request, without a ticket to the platform team.

### Why the words matter

Each one names a boundary: what the platform owns, what the team owns, and where the ticket queue used to be. Get them wrong and you build a portal nobody uses.

> **The honest caveat:** a platform without a golden path is a portal with links. The path is the product.

> **The lesson:** platform teams ship products, and developers are the users.

## In one line

> **A platform is a product.** Its users are developers, and its competition is a ticket queue.

**Read the docs:** backstage.io/docs
