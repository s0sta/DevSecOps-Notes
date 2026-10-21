---
id: p378
title: "Anatomy of a CVSS vector"
slug: anatomy-of-a-cvss-vector
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CVSS, CyberSecurity, RiskManagement, DevSecOps, AppSec]
source: "LinkedIn post P378 · DevSecOps series"
linkedin_date: 2029-02-25
design: anatomy
---

# Anatomy of a CVSS vector

Two findings arrive on the same day, both called critical. One needs a click from an admin; the other needs nothing but a browser. The vector is where that difference lives, and six segments carry it.

## Quick reference

```text
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
```

| Part | Name | What it means |
|:--|:--|:--|
| `CVSS:3.1` | Version | The scoring system in use. v3.1 and v4.0 do not score the same flaw alike. |
| `AV:N` | Attack vector | Network: reached over a network, not from a keyboard in the lobby. |
| `AC:L` | Attack complexity | Low: no race to win, no special configuration, no lucky timing. |
| `PR:N` | Privileges required | None: the attacker starts unauthenticated. |
| `UI:N` | User interaction | None: no link to click, no file to open, no prompt to approve. |
| `S:U/C:H/I:H/A:H` | Scope and impact | Scope unchanged; confidentiality, integrity and availability all High. |

## Explained

**The prefix**  
CVSS:3.1 names the scoring system. Version 3.1 and version 4.0 do not produce the same number from the same flaw, so a score without a version is a rumour. It looks like decoration; it is the first thing to check.

**The attack path**  
AV:N is network: the attacker reaches the service over a network, not from a keyboard in the lobby. Adjacent, local and physical are the other three values.  
AC:L is low complexity: no race to win, no special configuration, no lucky timing. High complexity means the attacker must meet a condition you do not control.  
PR:N is no privileges: the attacker starts unauthenticated.  
UI:N is no user interaction: nobody has to click a link, open a file or approve a prompt.

**Scope and impact**  
S:U is scope unchanged, so the flaw stays inside one security authority. C:H, I:H and A:H are high impact on confidentiality, integrity and availability. This vector scores 9.8 and lands in the critical band.

> **The honest caveat:** the base vector ignores your environment. A network-only service with no data behind it can carry a 9.8 that means nothing in your estate. Temporal and environmental metrics exist; most teams never fill them in.

> **The lesson:** read the vector before you argue about the score; the fields are the argument.

## In one line

> **A vector is a sentence.** Every field answers a different question about the same flaw.

**Read the vector:** nvd.nist.gov/vuln-metrics/cvss
