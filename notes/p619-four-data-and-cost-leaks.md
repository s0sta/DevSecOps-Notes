---
id: p619
title: "Four data and cost leaks"
slug: four-data-and-cost-leaks
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [CloudCost, FinOps, SRE, DevOps, DataProtection]
source: "LinkedIn post P619 · PythonFixes series"
linkedin_date: 2030-09-10
design: explainer
---

# Four data and cost leaks

A cost review finds four leaks in one afternoon, and none of them looks like a mistake on the day it is made.

## Quick reference

### Untested backups

- A copy that never restored is a hypothesis
- The dashboard is green, the restore is not
- One drill a month is the cheapest test

### Unbounded logs

- Retention by size, not by hope
- One chatty service can fill a disk
- The archive is a second bill

### Cold data in hot storage

- Standard bills every idle byte
- Requests per GB decides the class
- Move it, then delete the source

### Orphaned volumes

- An unattached disk bills the same
- An idle IP bills by the hour
- A snapshot with no owner is forever

> **Note:** Each leak is invisible until the invoice arrives.

## Explained

### Untested backups

A copy that never restored is a hypothesis. The job writes a file, the dashboard turns green, and the first real test is the incident. The bill is not the problem here; the recovery time is.

### Unbounded logs

Retention by size, not by hope. One chatty service fills a disk, the archive becomes a second bill, and the useful line is buried in a terabyte. A policy with a number is the fix.

### Cold data in hot storage

Standard bills every idle byte. A bucket with a few requests per GiB is paying the hot price for cold data, and the invoice never names the bucket. Move it, then delete the source copy.

### Orphaned volumes

An unattached disk bills the same as a busy one. An idle address bills by the hour, a snapshot with no owner lives for ever, and nobody sees the line because it belongs to the account, not the team.

> **The honest caveat:** a leak is only a leak if nobody owns it. Some cold data is hot for a week, and some orphans are disaster-recovery copies that must stay.

> **The lesson:** data costs money after it stops being useful, not while it is.

## In one line

> **Nothing leaks faster than storage.** Four leaks that never show up as a line item with an owner.

**Count the orphans**

```bash
python3 orphan_resources.py inv.json
```
