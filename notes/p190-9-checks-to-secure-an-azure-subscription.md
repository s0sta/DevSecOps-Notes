---
id: p190
title: "9 checks to secure an Azure subscription"
slug: 9-checks-to-secure-an-azure-subscription
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Azure, AZ104, CloudSecurity, CyberSecurity, CloudGovernance]
source: "LinkedIn post P190 · Cloud / DevSecOps series"
linkedin_date: 2027-12-14
design: checklist
---

# 9 checks to secure an Azure subscription

Securing an Azure subscription is both an AZ-104 topic and the thing that keeps a cloud account from becoming a headline. Nine checks, grouped by what attackers and surprise bills actually exploit.

## Quick reference

### Identity

- **MFA for every user** — Conditional Access
- **Few Global Admins** — and use PIM for just-in-time
- **No standing owner on resources** — grant roles, not ownership

### Governance

- **Budget + cost alerts** — on day one
- **Azure Policy baseline** — deny public IPs, enforce tags
- **Resource locks on prod** — CanNotDelete on key groups

### Visibility

- **Defender for Cloud on** — free tier at least
- **Activity logs retained** — and exported
- **NSG flow logs** — see what is really talking

## Explained

### Identity

MFA for every user, enforced through Conditional Access. Identity is the real perimeter in the cloud; a password alone is not enough for anyone.  
Few Global Admins, and use Privileged Identity Management so even admins get their rights just-in-time, not permanently. Fewer standing admins, smaller blast radius.  
No standing ownership on resources. Grant specific roles at the right scope instead of handing out Owner, which can do anything including grant more access.

### Governance

Budget and cost alerts on day one. A compromised account mining crypto, or a forgotten cluster, both show up on the bill first.  
An Azure Policy baseline: deny public IPs where they are not needed, enforce tags, restrict regions. Policy stops mistakes before they happen.  
Resource locks on production. A CanNotDelete lock on critical resource groups prevents an accidental deletion.

### Visibility

Microsoft Defender for Cloud on, at least the free tier, for a secure-score and recommendations.  
Activity logs retained and exported, so you can investigate later. You cannot analyse what you never recorded.  
NSG flow logs, to see what is actually talking to what on the network.

> **The theme is simple:** least privilege on identity, guardrails on governance, and enough logging to see trouble.

## In one line

> **Least privilege, full visibility.** Identity and cost are where cloud accounts get hurt.

**First two moves:** MFA everywhere, then a budget alert
