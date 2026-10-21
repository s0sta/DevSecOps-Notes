---
id: p747
title: "The prioritisation ladder: signal, context, decision"
slug: the-prioritisation-ladder-signal-context-decision
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, RiskManagement, CyberSecurity, EPSS, CISAKEV]
source: "LinkedIn post P747 · ASM series"
linkedin_date: 2031-07-06
design: architecture
---

# The prioritisation ladder: signal, context, decision

A queue sorted by CVSS is sorted by the least relevant number in the room. Prioritisation is a ladder, and the rungs are not interchangeable: each one removes an assumption the rung above could not check.

## Quick reference

- **Tier 1 · Signal:** CVE record (CVE) · CVSS base (CVSS) · EPSS score (EPSS)
- **Tier 2 · Context:** KEV catalog (KEV) · Asset exposure (ASSET) · Reachability (REACH)
- **Tier 3 · Decision:** Ranked queue (RANK) · Owner and date (OWNER) · Exception log (EXC)

**Request flow:** CVE record → CVSS base; CVE record → EPSS score → Ranked queue → Owner and date; Ranked queue → Exception log; KEV catalog → Ranked queue; Asset exposure → Ranked queue; Reachability → Ranked queue

**Around it:** Scanner exports (SCAN) · Asset CMDB (CMDB) · EPSS daily feed (FEED) · KEV feed (KEV)

## Explained

### Signal

Signal is what the record says on its own. The CVE identifies the flaw, CVSS scores the severity of the code, and EPSS estimates the probability of exploitation in the next 30 days. None of the three knows where the code runs, so none can tell you whether it matters here.

### Context

Context is what your estate adds. KEV says exploitation has been observed, exposure says whether the asset is reachable from the internet, and reachability says whether a live import path can execute the vulnerable package. This is the rung where a 9.8 can drop and a 6.5 can climb, and the only one where you learn something a stranger could not.

### Decision

Decision is a person, a date and a record. A ranked queue without an owner is a reading list; an owner without a date is a wish. The exception log is what keeps the ladder honest when the answer is not now.

Under the rungs sit the inputs: scanner exports, the asset CMDB, the daily EPSS feed and the KEV feed.

> **The honest caveat:** a ladder still needs someone to decide what the bottom rung is worth.

> **The lesson:** every step down the ladder removes an assumption, and the decision belongs at the bottom.

## In one line

> **Signal is not a decision.** Every rung down the ladder removes an assumption.

**Start at signal**

```bash
grep -c '^CVE-' kev.csv
```
