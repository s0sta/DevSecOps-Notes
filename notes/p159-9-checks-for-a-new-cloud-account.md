---
id: p159
title: "9 checks for a new cloud account"
slug: 9-checks-for-a-new-cloud-account
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [CloudComputing, CyberSecurity, AWS, DevOps, ITSecurity]
source: "LinkedIn post P159 · IT series"
linkedin_date: 2027-10-03
design: checklist
---

# 9 checks for a new cloud account

A brand-new cloud account is at its most vulnerable on day one, before anyone has thought about security. Nine checks to do before you build anything real.

## Quick reference

### Lock the root

- **MFA on the root user** — hardware or app, not SMS
- **Stop using root** — create an admin user instead
- **Rotate root keys away** — delete root access keys

### See everything

- **Audit logging on** — CloudTrail / activity log
- **Billing alerts set** — a budget with email alerts
- **Default region chosen** — and unused regions restricted

### Least privilege

- **No long-lived keys** — use roles and short tokens
- **Groups, not per-user grants** — assign policies to groups
- **Encrypt by default** — storage and volumes

## Explained

### Lock the root

MFA on the root user. The root or global-admin account can do anything, including closing the account. Protect it with a hardware key or authenticator app, never SMS.  
Stop using root. Create a separate admin user or role for daily work, and lock root away for the rare tasks that truly need it.  
Rotate root access keys away. Root should have no long-lived access keys at all. Delete them.

### See everything

Audit logging on. Turn on CloudTrail, Azure activity logs or the equivalent from the start, stored where it cannot be quietly deleted. You cannot investigate what you never recorded.  
Billing alerts set. A budget with email alerts is your early warning for both runaway resources and a compromised account mining crypto on your bill.  
Default region chosen, and regions you do not use restricted, so resources cannot be spun up unnoticed on the other side of the world.

### Least privilege

No long-lived keys. Prefer roles and short-lived tokens over access keys that live in files forever.  
Groups, not per-user grants. Attach policies to groups and put users in them, so access stays reviewable.  
Encrypt by default. Turn on default encryption for object storage and disks.

The economics are simple: an hour securing a fresh account is far cheaper than responding to a breached one.

## In one line

> **Day one is the cheapest day.** Securing a fresh account beats cleaning up a breached one.

**First two moves:** MFA on root, then a budget alert
