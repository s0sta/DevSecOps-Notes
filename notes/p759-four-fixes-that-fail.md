---
id: p759
title: "Four fixes that fail"
slug: four-fixes-that-fail
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, CyberSecurity, SRE, DevOps, RiskManagement]
source: "LinkedIn post P759 · ASM series"
linkedin_date: 2031-08-03
design: explainer
---

# Four fixes that fail

Four fixes fail the same way: the finding goes away and the risk does not.

## Quick reference

### Hidden finding

- The check that found it was disabled after the scan
- The finding leaves the report, not the host
- Pin the check list and diff it with the findings

### Exception rot

- Approved for a quarter, renewed four times
- The reason field still says temporary
- The date moves whenever the review arrives

### Wave too big

- Forty patches in one window, one rollback
- The board approves without reading the list
- Cap the wave and split it by service

### No verification

- The patch command returned 0 and the ticket closed
- The service was never restarted
- Close only after a rescan with the same checks

> **Note:** Most failed fixes are two of these at once, in the gap between the patch and the proof.

## Explained

### Hidden finding

The rescan runs fewer checks than the scan before. The finding disappears because the check that found it was disabled, not because the host changed. Pin the check list and compare it with the findings.

### Exception rot

The exception was approved for a quarter and renewed four times. Nobody remembers the reason, the owner has changed team, and the date keeps moving. Give it an owner, a reason and an expiry that only the risk owner can extend.

### Wave too big

The window holds forty patches because the team wants the backlog gone. The first failure rolls back the batch, and the next window is smaller. A wave is a size, not a mood: cap it and split it by service.

### No verification

The patch command returned 0, the ticket is closed, and the scan still shows the finding open: the package went to the wrong host, or nobody restarted the service. Closure needs a second scan with the same checks.

The poster draws four panels in a 2x2 grid, each with a drawing and three bullets, in the order a fix goes wrong. The note says most failed fixes are two of these at once.

> **The honest caveat:** a rescan with the same checks is evidence, not proof; an asset that left the scope looks fixed.

> **The lesson:** the fix fails in the gap between patch and proof.

## In one line

> **The fix fails in the gaps.** Four ways the finding goes away and the risk does not.

**Rescan before close**

```bash
python3 rescan_diff.py b.json a.json
```
