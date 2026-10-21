---
id: p760
title: "Fix now vs fix later"
slug: fix-now-vs-fix-later
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, RiskManagement, CyberSecurity, SRE, DevOps]
source: "LinkedIn post P760 · ASM series"
linkedin_date: 2031-08-05
design: matrix
---

# Fix now vs fix later

Three columns, six rows, one question: does this finding get fixed now, this sprint, or in the backlog?

## Quick reference

| | **Now** | **This sprint** | **Backlog** |
|:--|:--|:--|:--|
| Severity | Critical | High | Medium or low |
| Exposure | Internet-facing | Internal, reachable | Isolated |
| KEV | On the KEV list | Not listed, EPSS high | No exploit signal |
| Effort | Under an hour | Under a day | A project |
| Owner | Named owner | Team queue | No owner yet |
| Verification | Rescan same check | Rescan at close | Next scan cycle |

**How to pick**

- **Now** → fix inside the window, rescan the same check.
- **This sprint** → schedule it, then rescan at close.
- **Backlog** → review it at the next scan cycle.

## Explained

### The rows

Severity, exposure, KEV, effort, owner and verification. The matrix puts them side by side, so a critical finding with no owner and a week of work does not become a now item by accident. The columns are the answer; the rows are the evidence behind it.

### Now

Critical, internet-facing, on the KEV list, under an hour of work, a named owner and a rescan with the same check. Five of six is not a now item; it is a conversation about what is missing.

### This sprint

High, reachable from the internal network, no KEV hit but a high EPSS score, under a day of work, a team queue, a rescan before the close.

### Backlog

Medium or low, isolated, no exploit signal, a project-sized effort, no owner yet, verified at the next scan cycle. The backlog is where a finding waits for review, not where it is forgotten.

### The grid

The poster draws three columns and six rows, with the row labels down the left, a coloured header for each column and a pick box at the bottom.

> **The honest caveat:** KEV means exploitation has been observed, not that it is coming for you; EPSS estimates the chance and is not a verdict. The thresholds are policy choices, so write them down.

> **The lesson:** now is a decision you can defend, not a feeling you had on Monday.

## In one line

> **Now is a decision, not a default.** A deadline is a set of facts, not a mood on Monday.

**Date the fix**

```bash
python3 owner_brief.py f.json --owner api
```
