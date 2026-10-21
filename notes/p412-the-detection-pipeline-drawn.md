---
id: p412
title: "The detection pipeline, drawn"
slug: the-detection-pipeline-drawn
sections: [devsecops]
topic: "Incident response & detection"
tags: [DetectionEngineering, SIEM, IncidentResponse, DevSecOps, CyberSecurity]
source: "LinkedIn post P412 · DevSecOps series"
linkedin_date: 2029-05-15
design: architecture
---

# The detection pipeline, drawn

The 02:00 page named a host, a user and a command, and the on-call engineer had a runbook open before the coffee finished. That is not luck. It is three tiers of plumbing that existed before anyone was attacked.

## Quick reference

- **Sources:** Application logs (APP) · Cloud audit trail (AUDIT) · CI logs (CI)
- **Detect:** SIEM rules (RULE) · Correlation (CORR)
- **Respond:** Alert (PAGE) · Runbook (RUN) · Containment (HOLD)

**Request flow:** Application logs → SIEM rules → Correlation → Alert → Runbook → Containment; Cloud audit trail → SIEM rules; CI logs → Correlation

## Explained

### Sources

Application logs carry requests, authentication events and the errors the code chose to print. The cloud audit trail records every management API call with the identity, the source address and whether it succeeded. CI logs record deploys, token use and the jobs that touched production. If a source is missing, the tier above it has nothing to match.

### Detect

SIEM rules match one event: a root login, a policy change, a key created outside the change window. Correlation joins several events inside a window, so a burst of failed logins followed by one success becomes a signal rather than two hundred rows. Rules are code: versioned, reviewed and replayed against a fixture before they page anyone.

### Respond

The alert carries severity, the evidence and a link to the runbook. The runbook names the first three moves: verify the finding, scope what else the identity touched, revoke or isolate. Containment is the last tier, and the one that buys the investigation its time.

> **The honest caveat:** detection is bounded by what the application logs and how long it is kept. Buying a SIEM does not create the log line that was never written.

> **The lesson:** detection is a pipeline, and its slowest tier sets the response time.

## In one line

> **A log line is a promise to act.** Three tiers stand between the event and the response.

**Trace one alert**

```bash
jq '.Records[0].eventName' trail.json
```
