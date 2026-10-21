---
id: p417
title: "Anatomy of an audit event"
slug: anatomy-of-an-audit-event
sections: [devsecops]
topic: "Incident response & detection"
tags: [CloudTrail, AWS, DetectionEngineering, IncidentResponse, DevSecOps]
source: "LinkedIn post P417 · DevSecOps series"
linkedin_date: 2029-05-27
design: anatomy
---

# Anatomy of an audit event

One line from the audit trail is enough to open an investigation, if you know which six fields to read. The line is normalised for the poster: raw CloudTrail spreads these facts across userIdentity, errorCode and awsRegion.

## Quick reference

```text
AssumeRole user=deploy 10.0.4.7 mfa=false result=Denied eu-west-1
```

| Part | Name | What it means |
|:--|:--|:--|
| `AssumeRole` | Event | The API call. A rule matches this field first. |
| `user=deploy` | Identity | The role or IAM user behind the call. |
| `10.0.4.7` | Source IP | Where the call came from. Compare it with the baseline. |
| `mfa=false` | MFA used | Whether the session presented a second factor. |
| `result=Denied` | Result | Denied means errorCode was set; nothing changed. |
| `eu-west-1` | Region | The region targeted. Drift from the usual one is a signal. |

## Explained

### The six fields

AssumeRole is the event name, the call that hands out temporary credentials, and the first field a rule matches. `user=deploy` is the identity: a role or an IAM user, and the difference matters, because a role can be assumed by anything that can reach its trust policy. 10.0.4.7 is the source address, a number on its own and a location against the baseline; this one sits in the build subnet, so a call from here at 02:00 is worth a look.

`mfa=false` is the flag that turns a suspicious login into a finding, because the session presented no second factor. `result=Denied` means an errorCode was set and the call changed nothing, though a run of denied calls from one identity is a script learning the permissions it lacks. eu-west-1 is the region, and a call from a region the account has never used is the cheapest anomaly to alert on.

### Why the line works

A rule reads the fields together: AssumeRole, no MFA, denied, from a new region. Any single field is a fact; the combination is a detection.

> **The honest caveat:** this is a display form, not the API shape. Build the parser on Records, userIdentity.type and errorCode, then format the line.

> **The lesson:** a detection rule is only as good as the fields it can name.

## In one line

> **One line, six fields to check.** The fields separate a fact from a finding.

**Read one record**

```bash
jq '.Records[0].eventName' trail.json
```
