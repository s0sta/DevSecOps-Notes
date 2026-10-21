---
id: p402
title: "The request security path, drawn"
slug: the-request-security-path-drawn
sections: [devsecops]
topic: "Application & API security"
tags: [AppSec, APISecurity, DevSecOps, CyberSecurity, WebSecurity]
source: "LinkedIn post P402 · DevSecOps series"
linkedin_date: 2029-04-22
design: architecture
---

# The request security path, drawn

A request arrives with a valid session, a plausible body and a familiar path. Nothing about it looks hostile. The only question is how many layers inspected it before your data.

## Quick reference

- **Edge:** WAF (WAF) · Rate limit (429)
- **App:** Authentication (401) · Authorisation (403) · Input validation (VAL)
- **Data:** Parameterised query (SQL) · Encrypted store (AES)

**Request flow:** WAF → Rate limit → Authentication → Authorisation → Input validation → Parameterised query → Encrypted store

## Explained

### Edge

The first tier is the edge. A WAF matches the request against rules for known payloads and blocks the obvious attempts before they cost you a worker. A rate limit caps how many requests one client can send, so a credential-stuffing run or a scraper gets a 429 instead of your database. Neither knows your business logic.

### Application

The second tier is the application. Authentication proves who is calling: a missing or invalid token gets a 401. Authorisation decides what that identity may touch, and a valid session asking for another tenant's order gets a 403. Input validation then rejects anything that does not match the expected shape, type and length. The three run in that order, because identity without permission is still a stranger.

### Data

The third tier is the data. The parameterised query keeps the value separate from the SQL, so a quote in a name cannot become syntax. The encrypted store protects the rows if a backup or a disk leaves the building.

> **The honest caveat:** layers do not add up to safety. A WAF rule can be bypassed, a rate limit is per key, and an internal service that trusts its caller skips the edge entirely.

> **The lesson:** each layer answers a different question, and no layer answers all of them.

## In one line

> **Every layer says no in its own way.** A request that survives all three is the only one that reaches data.

**Trace one request**

```bash
curl -sv https://api.example.com/me
```
