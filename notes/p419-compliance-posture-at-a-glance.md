---
id: p419
title: "Compliance posture at a glance"
slug: compliance-posture-at-a-glance
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Compliance, GRC, CyberSecurity, DevSecOps, ISO27001]
source: "LinkedIn post P419 · DevSecOps series"
linkedin_date: 2029-05-31
design: dashboard
---

# Compliance posture at a glance

The auditor asked for three things and the team produced a spreadsheet, a screenshot and an apology. Compliance is a maintenance programme, and these six tiles are what maintenance looks like.

## Quick reference

**Status:** Q4

| Metric | Value | Note |
|:--|:--|:--|
| Controls passing | **92%%** | of 148 controls |
| Evidence current | **88%%** | refreshed this quarter |
| Open exceptions | **4** | 2 expire this month |
| Last audit | **12 days** | external, ISO 27001 scope |
| Findings closed | **37** | of 41 from the audit |
| Owner coverage | **96%** | of assets with a named owner |

## Explained

### The register

Controls passing: ninety-two percent of 148, so 136 controls have evidence behind them this quarter. The twelve that do not are the agenda: a control that passes on paper is worse than a red one.

Evidence current: eighty-eight percent refreshed this quarter. Evidence has a shelf life: a screenshot from February proves February, and an auditor will ask for the date on the file.

Open exceptions: four, two expiring this month. An exception is a decision with a date on it; one without an expiry is a permanent hole with a ticket number.

### The audit

Last audit: twelve days ago, external, ISO 27001 scope. The date matters less than the findings list it produced, because the list is the work plan for the next quarter.

Findings closed: thirty-seven of forty-one. Closure rate is the honest measure of a compliance programme, and the four that remain are the ones to talk about first.

### The owners

Owner coverage: ninety-six percent of assets have a named owner. The last four percent are the assets nobody will claim, and those are the ones an attacker finds.

> **The honest caveat:** a passing control is a snapshot of the day it was tested. Drift between audits is normal, which is why the exceptions register, not the pass rate, is where the truth lives.

> **The lesson:** compliance is maintained between audits, not demonstrated during them.

## In one line

> **Evidence first, opinions later.** A control is a claim until the evidence is in the folder.

**Check the register**

```bash
grep -c 'open' register.csv
```
