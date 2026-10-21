---
id: p727
title: "The surface map"
slug: the-surface-map
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, AttackSurface, ASM, DevSecOps, CloudSecurity]
source: "LinkedIn post P727 · ASM series"
linkedin_date: 2031-05-20
design: architecture
---

# The surface map

Every attack surface programme starts with the same argument: the scanner says one thing, the CMDB another, and the spreadsheet a third. The map that ends it has three tiers, each answering a different question.

## Quick reference

- **Discover:** Certificate log (CT) · DNS export (DNS) · Port scan (PORT)
- **Inventory:** CMDB (CMDB) · Owner map (OWN) · Cost centre (COST)
- **Score:** Exposure (EXPO) · Risk (RISK)

**Request flow:** Certificate log → CMDB → Owner map → Exposure → Risk; CMDB → Cost centre → Risk; DNS export → CMDB; Port scan → CMDB

**Around it:** crt.sh export (JSON) · dig export (CSV) · CMDB export (CSV) · Owner tag (TAG)

## Explained

### Discover

The bottom tier is evidence. Certificate transparency gives you every name a CA has ever issued for, including the staging host that never reached DNS. The DNS export gives you the records that exist now, with their status. A port scan gives you what answers on the ranges you own. No source trusts another, which is the point: three independent views of the same estate.

### Inventory

The middle tier turns names into assets. The CMDB says what the organisation believes it owns, the owner map says who agreed to it, and the cost centre says who pays. Most programmes stall here, because a host with no owner cannot be prioritised, patched or deleted.

### Score

The top tier is a decision. Exposure asks what the internet can reach, and risk asks what happens if it is reached. Both need the two tiers below: exposure without inventory is a port list, and risk without an owner is a number nobody accepts.

The tiers are a loop, not a stack. A score nobody owns goes back to inventory, and an unowned asset goes back to discovery until someone claims it.

> **The honest caveat:** the map is only as good as the exports. A tier that reads a stale CSV produces a confident answer about last month.

> **The lesson:** discover, attribute, score, in that order, and never skip the middle.

## In one line

> **Discover, attribute, then score.** Three tiers, one loop, and no tier trusts the one below it.

**Start at discover**

```bash
python3 ct_inventory.py ct.json
```
