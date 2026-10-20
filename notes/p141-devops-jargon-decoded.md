---
id: p141
title: "DevOps jargon, decoded"
slug: devops-jargon-decoded
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, CloudComputing, SRE, ITCareer, SoftwareEngineering]
source: "LinkedIn post P141 · IT series"
linkedin_date: 2027-08-22
design: reveal
---

# DevOps jargon, decoded

DevOps is full of acronyms that get used as if everyone already knows them. Here are six, in plain English, so the next standup makes more sense.

## Quick reference

- **CI** — Continuous Integration: every code push is built and tested automatically, so bugs are caught early.
- **CD** — Continuous Delivery or Deployment: tested code ships to production with little or no manual work.
- **IaC** — Infrastructure as Code: your servers and networks are defined in files you version, not clicks in a console.
- **SLO** — Service Level Objective: the reliability target you aim for, like 99.9% of requests succeed.
- **Idempotent** — Running it again changes nothing new. Safe to repeat, which is why automation relies on it.
- **Rollback** — Returning to the last known-good version fast, when a release goes wrong.

## Explained

CI, Continuous Integration. Every time someone pushes code, a pipeline automatically builds the project and runs the tests. The point is to catch problems within minutes of writing them, while the change is small and fresh, instead of during a painful merge weeks later.

CD, Continuous Delivery or Deployment. Once code passes CI, it moves toward production automatically. Continuous Delivery means it is always ready to release with one click. Continuous Deployment goes further and ships it with no human step at all.

IaC, Infrastructure as Code. Instead of clicking through a console to create servers, you describe them in files, like Terraform. Those files are versioned, reviewed and repeatable, so an environment can be rebuilt identically.

SLO, Service Level Objective. The reliability target you commit to, such as 99.9% of requests succeeding. It turns "the site should be reliable" into a number you can measure and make decisions against.

Idempotent. A fancy word for a simple idea: running something again makes no new change. Automation depends on this, because a script must be safe to re-run after a failure.

Rollback. Returning quickly to the last version that worked when a release breaks. A tested, one-command rollback is what makes frequent deploys safe.

Clear words build trust. If a term stays jargon, it stays a black box for the people around you.

## In one line

> **Clear words build trust.** If you cannot explain it simply, it stays a black box.

**Teach one today:** explain CI to someone new
