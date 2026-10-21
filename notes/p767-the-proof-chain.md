---
id: p767
title: "The proof chain"
slug: the-proof-chain
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, CyberSecurity, GRC, DevSecOps, CISO]
source: "LinkedIn post P767 · ASM series"
linkedin_date: 2031-08-21
design: architecture
---

# The proof chain

Every quarter the team presents a clean dashboard, and every quarter the auditor asks the same question: show me the proof, dated and owned.

## Quick reference

- **Measure:** Trend report (TREND) · Coverage report (COV)
- **Map:** Control map (CTL) · Owner register (OWN)
- **Attest:** Audit packet (PACK) · Sign-off record (SIGN)

**Request flow:** Coverage report → Owner register → Sign-off record → Trend report → Control map → Audit packet

**Around it:** Findings export (FIND) · Scan history (SCAN) · Evidence store (EVID)

## Explained

### The three tiers

Measure holds the trend report and the coverage report: is the backlog shrinking, and was every asset scanned by every required tool. Map holds the control map and the owner register: which control each finding belongs to, and who closes it. Attest holds the audit packet and the sign-off: the dated evidence, indexed by control, and a named person who accepts it.

### The arrows

Trend and coverage feed the map, because a gap with no owner is not actionable. The map feeds the packet, because evidence without a control id cannot be filed. The signed packet returns to measure as next quarter's baseline; that loop is what makes it a chain rather than three reports. Below the tiers sit the inputs: the findings export, the scan history and the evidence store.

### How to use it

Give each tier one weekly output and one owner, reviewed on the same day, in the same hour. If a link is missing, stop and fix it: an attestation over an unscanned estate is a signature on a guess.

> **The honest caveat:** the chain is only as strong as the weakest link, and a signed packet cannot repair a blind asset or an unowned gap.

> **The lesson:** proof is a chain, not a slide.

## In one line

> **Proof is a chain, not a slide.** A signed packet over an unscanned estate is a signature on a guess.

**Follow the chain**

```bash
python3 trend_report.py history.json
```
