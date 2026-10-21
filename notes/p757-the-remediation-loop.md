---
id: p757
title: "The remediation loop"
slug: the-remediation-loop
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, DevOps, CyberSecurity, SRE, Automation]
source: "LinkedIn post P757 · ASM series"
linkedin_date: 2031-07-29
design: architecture
---

# The remediation loop

The remediation loop has three tiers, and every finding travels through all of them or it does not close.

## Quick reference

- **Plan:** Wave plan (WAVE) · Owner map (OWN) · Due dates (DUE)
- **Execute:** Patch window (PATCH) · Exception (EXC) · Change record (CHG)
- **Verify:** Rescan diff (DIFF) · Closure (CLOSE) · Escalation (ESC)

**Request flow:** Wave plan → Patch window → Rescan diff → Closure; Rescan diff → Escalation; Owner map → Patch window; Due dates → Escalation; Exception → Rescan diff

**Around it:** patch_waves.py (PY) · exception_register.py (PY) · rescan_diff.py (PY) · owner_brief.py (PY)

## Explained

### Plan

The first tier is the wave plan, the owner map and the due dates. A finding becomes work when it has an owner, a fix version and a due date. The plan groups by owner, service and fix version, and caps each wave so a change window can review it.

### Execute

The second tier is the patch window, the exception and the change record. The exception is the one row allowed to leave the loop, with an owner, a reason and an expiry. The change record links the ticket to the build that shipped.

### Verify

The third tier is the rescan diff, the closure and the escalation. The rescan runs the same checks as before and reports closed, still open, new and hidden. A closure is written only after the rescan, never after the patch command returns. Escalation catches the wave that missed its date.

### Read it in order

The poster draws the three bands top to bottom, with arrows from the wave plan and the owner map into the patch window, then to the rescan and the closure. The due dates and the rescan feed the escalation node, the loop's exit for a finding that will not close. Four chips at the bottom name the scripts.

> **The honest caveat:** the loop is only as fast as the scan, and a weekly scan makes a daily fix wait a week for proof.

> **The lesson:** plan, execute, verify, close, then plan again.

## In one line

> **Plan, execute, verify, close.** Three tiers, and a finding leaves only through the last one.

**Check the loop**

```bash
python3 rescan_diff.py b.json a.json
```
