---
id: p769
title: "Four reports that lie"
slug: four-reports-that-lie
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [Metrics, CyberSecurity, RiskManagement, VulnerabilityManagement, CISO]
source: "LinkedIn post P769 · ASM series"
linkedin_date: 2031-08-26
design: explainer
---

# Four reports that lie

None of these four reports is false. Each is true in a way that hides the thing it claims to show.

## Quick reference

### The vanity metric

- 1,842 findings closed this quarter
- 2,100 opened, so the backlog grew
- 48% closure with no denominator
- Fix: net flow and a denominator

### The unscanned asset

- Coverage on scans the scanner sent
- The database was never in the count
- A clean report over part of the estate
- Fix: join the inventory to the scans

### The unmapped finding

- High finding, no control id
- It cannot appear in the audit
- The framework looks fully covered
- Fix: map the category, then the finding

### The stale evidence

- The export is dated January
- The control changed in March
- The packet still passes review
- Fix: date every artefact you send

> **Note:** Each report is true on its own. Together they hide four different gaps.

## Explained

### The vanity metric

1,842 findings closed this quarter sounds like progress. Opened were 2,100, so the backlog grew and the closure rate of 48% has no denominator worth the name.

### The unscanned asset

Coverage is measured on scans sent, divided by the assets the scanner knew about. The database that was never added to the inventory is not a gap in the report; it is outside the population.

### The unmapped finding

A high finding with no control id cannot appear in the audit. The framework looks fully covered because the finding was never in the count.

### The stale evidence

The export is from January, the control changed in March, and the packet still passes review. The date is on the file; nobody reads it until the audit, and then it is too late.

### What they share

Each one measures what is easy to count, then presents it as the whole. The fix is the same in all four: name the population, the denominator and the date on the same line as the number.

> **The honest caveat:** a simple metric is not a lie. It becomes one when it is presented as the whole picture.

> **The lesson:** a report is a claim; make it show its working.

## In one line

> **A report can be true and useless.** A number without its population is a claim without its evidence.

**Check the claim**

```bash
python3 trend_report.py h.json
```
