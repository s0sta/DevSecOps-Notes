---
id: p374
title: "The threat modelling cheat sheet"
slug: the-threat-modelling-cheat-sheet
sections: [devsecops]
topic: "Application & API security"
tags: [ThreatModelling, DevSecOps, CyberSecurity, AppSec, SecureSDLC]
source: "LinkedIn post P374 · DevSecOps series"
linkedin_date: 2029-02-15
design: cheatsheet
---

# The threat modelling cheat sheet

The blank threat-model page is why most teams skip threat modelling. They open a template, read the headings, and close it again.

## Quick reference

### STRIDE

```bash
Spoof or tamper: who can act or alter?
Repudiate: what is never logged?
Disclose: what leaks in an error?
Deny: what has no rate limit?
Elevate: what runs as root?
```

### Boundaries

```bash
Draw the edge: browser, API, data
Mark every place trust changes
List each entry point and its auth
Name the asset behind each flow
Give every boundary an owner
```

### Data flows

```bash
Trace one request end to end
Label the data on every arrow
Mark where it is encrypted
Note where it is logged
Find the flow with no auth check
```

### Mitigations

```bash
Validate input at the boundary
Parameterise every SQL query
Rate limit by identity and route
Log the deny and alert on it
Add one test per named threat
```

## Explained

**STRIDE**  
STRIDE gives the questions their names: spoofing, tampering, repudiation, information disclosure, denial of service and elevation of privilege. The sheet pairs them with prompts you can ask out loud: who can act or alter, what is never logged, what leaks in an error, what has no rate limit, what runs as root. Spoofing and tampering share one line because both ask who can act or alter what.

**Boundaries**  
Boundaries asks where trust changes. Draw the edge from browser to API to database, mark every boundary, list the entry points and their authentication, name the asset behind each flow, and give every boundary an owner.

**Data flows**  
Data flows asks what moves. Trace one request end to end, label the data on every arrow, mark where it is encrypted and where it is logged, and find the flow with no auth check.

**Mitigations**  
Mitigations asks what you will do. Validate at the boundary, parameterise every query, rate limit by identity and route, log the deny and alert on it, and add one test per named threat.

> **The honest caveat:** these are prompts, not answers. A prompt becomes a threat model only when a named person writes down the mitigation and the test that proves it.

> **The lesson:** the quality of a threat model is the quality of its questions, and every question needs an owner.

## In one line

> **Ask better questions.** A threat model is a list of questions with owners.

**Start with a diagram:** draw the data flow first
