---
id: p186
title: "6 Azure numbers worth knowing"
slug: 6-azure-numbers-worth-knowing
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [Azure, AZ104, CloudComputing, CostOptimization, CloudCareer]
source: "LinkedIn post P186 · Cloud / DevSecOps series"
linkedin_date: 2027-12-05
design: numbers
---

# 6 Azure numbers worth knowing

A few numbers make Azure, and the AZ-104 exam, much less intimidating. Six worth keeping in your head.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **$200** | Free account credit | Spend it on a 30-day lab, then use always-free services. | free |
| **700** | AZ-104 pass score | Out of 1000. Scaled, so not a simple percentage. | exam |
| **3** | Availability Zones | Most regions have 3, for surviving a datacenter failure. | HA |
| **99.99%** | VM SLA (multi-AZ) | Spread VMs across zones to earn the higher SLA. | SLA |
| **65+** | Always-free services | Services with a free tier beyond the 30-day credit. | free |
| **5 min** | Delete a lab | The habit that keeps your free credit alive. | cost |

## Explained

$200, the free account credit. A new Azure account gives you $200 to spend in the first 30 days. That is more than enough for a full AZ-104 lab: VMs, networking, storage and identity. After the 30 days, you drop to the always-free services.

700, the AZ-104 pass score. Microsoft exams are scored from 1 to 1000, and 700 is the pass mark. It is scaled, not a raw percentage, so do not assume 70% of questions. Practice assessments are the best gauge.

3, availability zones. Most major Azure regions have three physically separate zones. Spreading resources across them is how you survive a single datacenter failure, and it is a core AZ-104 concept.

99.99%, the VM SLA. You only get the top availability SLA when VMs are spread across zones. A single VM has a much lower guarantee. The architecture earns the SLA, not the VM type.

65+, always-free services. Beyond the 30-day credit, Azure has dozens of services with a standing free tier, enough to keep learning without spending.

5 minutes, to delete a lab. The single habit that protects your credit and your wallet: put everything in a resource group and delete it when you are done.

> **The theme:** respect the free limits, and nothing on this list costs you money.

## In one line

> **Know the limits, keep the credit.** Most Azure bill shocks are a lab nobody deleted.

**Guard the bill:** set a budget alert on day one
