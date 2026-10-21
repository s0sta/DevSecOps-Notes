---
id: p750
title: "9 checks before you call a finding critical"
slug: 9-checks-before-you-call-a-finding-critical
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, RiskManagement, CyberSecurity, AppSec, DevSecOps]
source: "LinkedIn post P750 · ASM series"
linkedin_date: 2031-07-13
design: checklist
---

# 9 checks before you call a finding critical

A finding gets called critical in a meeting, and the word does three jobs at once: it describes the bug, the asset and the urgency. Nine checks separate them, in three groups.

## Quick reference

### Severity

- **CVSS is 9.0 or higher** — base score, v3.1 or v4.0
- **EPSS is above the line** — policy, not truth
- **It is in KEV, or it is not** — check today's catalogue

### Reach

- **Package is imported live** — walk from entry points
- **The function is called** — grep the call site
- **No dynamic loading** — importlib, plugins

### Exposure

- **Asset is internet-facing** — CMDB, not guesswork
- **No auth in front of it** — SSO still counts
- **Data class is high** — PII, payments, keys

## Explained

### Severity

CVSS is 9.0 or higher, on the base score, and you know whether it is v3.1 or v4.0, because the two do not compare cleanly. That is a judgement about the code, and the only group a scanner can answer alone. EPSS is above the line you agreed, and the line is policy, not truth. And you have checked today's KEV catalog, so you know whether this is exploited or merely severe.

### Reach

The package is imported on a live path, walked from a real entry point. The vulnerable function is actually called, which a grep of the call site usually settles. And nothing loads the module dynamically: importlib, plugins and template loaders all defeat a static graph.

### Exposure

The asset is internet-facing, according to the CMDB rather than a guess. No authentication sits in front of it, and SSO counts as authentication even when it is one password away. The data class is high: personal data, payments or keys.

> **The honest caveat:** a checklist makes the decision explainable, not correct. Someone still has to own the date.

> **The lesson:** critical is a claim about consequence, and consequence needs an asset.

## In one line

> **Critical is a decision, not a score.** Nine questions turn a severity into a sentence someone can act on.

**The first check**

```bash
grep CVE-2024-3400 kev.csv
```
