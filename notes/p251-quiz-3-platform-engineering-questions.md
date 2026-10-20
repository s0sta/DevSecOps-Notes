---
id: p251
title: "Quiz: 3 platform engineering questions"
slug: quiz-3-platform-engineering-questions
sections: [devsecops]
topic: "Platform engineering"
tags: [PlatformEngineering, DevOps, SRE, CloudNative, CICD]
source: "LinkedIn post P251 · Platform series"
linkedin_date: 2028-05-04
design: quiz
---

# Quiz: 3 platform engineering questions

Platform engineering is easy to describe and hard to judge. Three questions separate a real platform from a rebranded ticket queue. Answer before you read on.

## Quick reference

**Q1. What makes a golden path succeed?**

- a) It is mandatory for every team
- b) It is the fastest supported way to ship
- c) It replaces the platform team

> **Answer:** b) It is the fastest supported way to ship. A golden path is a product. If it is slower or harder than the free-for-all, teams route around it, and the platform loses the signal it needs to improve.

**Q2. Why keep a service catalog instead of a spreadsheet?**

- a) It stores more columns per service
- b) It links owner, docs and runtime
- c) It replaces incident management

> **Answer:** b) It links owner, docs and runtime. A catalog makes the owner, API, runbook and dependencies discoverable in one entity. A spreadsheet copies stale facts with no link to the running system.

**Q3. When should you build a platform tool instead of buying it?**

- a) Always, to avoid licence fees
- b) When it is core to how you differentiate
- c) Never, managed services are cheaper

> **Answer:** b) When it is core to how you differentiate. Build where your constraints are different and the capability is strategic. Buy the commodity layers, where a vendor carries upgrades and on-call.

## Explained

### Question one

What makes a golden path succeed? It is the fastest supported way to ship, not the only allowed one. A golden path is a product with users. If it is slower or harder than the free-for-all, teams route around it, and the platform team loses the telemetry it needs to improve. Making it mandatory hides that signal; making it faster earns adoption.

### Question two

Why keep a service catalog instead of a spreadsheet? Because it links the owner, the docs, the API and the runtime in one entity. A spreadsheet copies facts that go stale, and it cannot answer "who owns this and is it healthy?" from the same place as the alert. Backstage's catalog is a graph, not a table.

### Question three

When should you build a platform tool instead of buying it? When it is core to how the company differentiates, or when the constraint is genuinely unusual. Build the thin layer that encodes your rules; buy the commodity underneath, where a vendor carries upgrades and on-call. Building a database because you dislike the licence is not platform engineering.

> **The honest caveat:** all three answers depend on adoption. A catalog nobody updates and a path nobody uses are both expensive decoration.

> **The lesson:** a platform is judged by what teams do, not by what it ships.

## In one line

> **Make the right way the easy way.** A platform is judged by what teams do, not what it ships.

**Ship one path:** template + CI + docs
