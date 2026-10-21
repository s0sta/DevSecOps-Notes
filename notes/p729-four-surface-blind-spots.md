---
id: p729
title: "Four surface blind spots"
slug: four-surface-blind-spots
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, AttackSurface, ASM, CloudSecurity, ITAM]
source: "LinkedIn post P729 · ASM series"
linkedin_date: 2031-05-25
design: explainer
---

# Four surface blind spots

Four assets stay invisible after a scan, and none of them is a scanner problem. They are process problems that leave a record behind, and each has a different fix.

## Quick reference

### Forgotten subdomain

- A staging host from a 2023 pilot, still resolving
- It never reached the CMDB or the pentest scope
- CT shows it the day its certificate is issued
- Fix: delete the record, or give it an owner

### Dangling CNAME

- The record points at a SaaS name nobody claimed
- The provider serves a claim page to anyone
- A suffix match is a lead; the marker is proof
- Fix: remove the CNAME, or claim the name first

### Unowned asset

- The scanner sees it; no team will admit to it
- No owner means no patch window and no budget
- A cost centre is not an owner, it is a chargeback
- Fix: name a person, not a mailbox

### Shadow account

- A shared cloud account with no CMDB entry
- Discovered assets run ahead of registered ones
- Age since first seen is the exposure clock
- Fix: reconcile weekly, and reconcile both ways

> **Note:** Four ways an asset hides after you have already scanned it.

## Explained

### Forgotten subdomain

A staging host from a 2023 pilot still resolves and accepts logins. It never reached the CMDB because the pilot had no ticket, and never reached a pentest scope because the scope came from the CMDB. Certificate transparency finds it the day the certificate is issued.

### Dangling CNAME

The record points at a SaaS name nobody claimed. The provider serves a claim page to anyone who asks, and the subdomain comes with it. A suffix match is a lead, not a finding: the marker on the claim page is the evidence.

### Unowned asset

The scanner sees it, and no team will admit to it. No owner means no patch window, no budget and no one to accept the risk. A cost centre is a chargeback code, not an owner.

### Shadow account

A shared cloud account with no CMDB entry, where discovery runs ahead of registration. The age since first seen is the exposure clock, and an unreviewed account is where a test database becomes customer data.

> **The honest caveat:** two of these can be true at once. The forgotten subdomain is usually the dangling CNAME, because the service behind it was retired first.

> **The lesson:** the scan finds the asset, and the process decides whether anyone owns it.

## In one line

> **Scanned is not the same as seen.** A scan finds the asset; a process decides who owns it.

**Delete or own**

```bash
dig +short old.acme.com
```
