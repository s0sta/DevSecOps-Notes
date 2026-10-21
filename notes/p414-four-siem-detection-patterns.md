---
id: p414
title: "Four SIEM detection patterns"
slug: four-siem-detection-patterns
sections: [devsecops]
topic: "Incident response & detection"
tags: [SIEM, DetectionEngineering, CyberSecurity, CloudSecurity, DevSecOps]
source: "LinkedIn post P414 · DevSecOps series"
linkedin_date: 2029-05-20
design: explainer
---

# Four SIEM detection patterns

Four alerts fire on the same Tuesday, and only one is an incident. The difference is the pattern behind the rule, and every pattern needs a normal.

## Quick reference

### Brute force

- Many failed logins, one account, short window
- Ten 4625 events in five minutes is a start
- The success after the burst is the real alert

### Impossible travel

- Two logins, two cities, less time than a flight
- Compare the source IP, the clock and the distance
- VPN egress and carrier NAT make this noisy

### Privilege escalation

- A policy attach outside the change window
- CreateAccessKey, AttachRolePolicy, AddUserToGroup
- Watch the first admin action after the grant

### Data exfiltration

- A read spike, then a transfer to a strange host
- S3 GetObject volume, then a large egress bill
- Baseline the account, then alert on the change

> **Note:** Each pattern is a baseline plus a threshold; the baseline is the hard part.

## Explained

### Brute force

Many failed logins, one account, a short window. Ten Windows 4625 events in five minutes is a start, and the same count of failed passwords in `auth.log` is the Linux version. The real alert is the success after the burst.

### Impossible travel

Two logins, two cities, less time than a flight takes. Compare the source IP, the clock and the distance, and set a speed no human reaches. VPN egress and carrier NAT break the geography, so this pattern produces more false positives than the other three.

### Privilege escalation

The signal is a policy attach outside the change window. CreateAccessKey, AttachRolePolicy and AddUserToGroup are the three calls that hand out or keep power, and the signal is the first admin action after the grant.

### Data exfiltration

A read spike, then a transfer to a strange host. S3 GetObject volume and the egress bill are the two numbers to baseline, per account and per hour. Alert on the change from the normal, because a large number on a busy account is not the same as a large number on a quiet one.

> **The honest caveat:** impossible travel is the weakest of the four. A VPN makes one person look like two, and a shared office makes two people look like one.

> **The lesson:** a pattern is a baseline plus a threshold, and the baseline is the part you have to earn.

## In one line

> **A pattern is a baseline first.** The rule is the easy half; the normal is the other half.

**Check the window**

```bash
grep -c 4625 security.log
```
