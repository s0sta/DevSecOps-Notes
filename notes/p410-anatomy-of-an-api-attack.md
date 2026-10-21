---
id: p410
title: "Anatomy of an API attack"
slug: anatomy-of-an-api-attack
sections: [devsecops]
topic: "Application & API security"
tags: [APISecurity, AppSec, CyberSecurity, IncidentResponse, DevSecOps]
source: "LinkedIn post P410 · DevSecOps series"
linkedin_date: 2029-05-10
design: timeline
---

# Anatomy of an API attack

Most API breaches do not begin with a zero-day. They begin with an endpoint that answers a question it should have refused, and a script that keeps asking.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **T+0** | Recon | Swagger, JS bundles and error messages map the API. |
| **T+2h** | Auth bypass | A valid token asks for another tenant's object and gets it. |
| **T+3h** | Data access | IDs are walked in order; each returns a full record. |
| **T+5h** | Exfiltration | A script pages through 40k records on the normal endpoint. |
| **T+9h** | Detection | A volume alert fires on one key, not on the endpoint. |
| **T+11h** | Containment | The key is revoked, the object check ships, 403 follows. |

## Explained

### The attack

T+0. Recon: the Swagger file, the JavaScript bundle and the error messages. Every field name and every ID format is a hint, and a public API document is a map.

T+2h. Auth bypass: a valid token asks for another tenant's object and receives it. The token is genuine; the check that the object belongs to the caller is missing. This is broken object level authorisation, and it needs no exploit.

T+3h. Data access: IDs are walked in order. Each response is a full record, so the attacker learns the shape of the data and which fields are sensitive.

T+5h. Exfiltration: a script pages through 40,000 records on the normal endpoint at a rate that looks like a busy customer. No malware, no unusual port, just GETs.

### The response

T+9h. Detection: a volume alert fires on one API key. The endpoint never alerted, because it was doing exactly what it was built to do.

T+11h. Containment: the key is revoked and the object check ships; the endpoint returns 403 for the other tenant. The log review then shows how far back the access goes.

> **The honest caveat:** this timeline is compressed. Real dwell time is usually weeks, and detection often arrives from a customer or a partner before it arrives from the SIEM.

> **The lesson:** an API does not need a vulnerability to leak; it needs a missing check and patience.

## In one line

> **The API answered every question.** Nothing was hacked. A missing check was used.

**Test one id**

```bash
curl -si $API/orders/1002 -b bob.txt
```
