---
id: p421
title: "Detection and response terms, decoded"
slug: detection-and-response-terms-decoded
sections: [devsecops]
topic: "Incident response & detection"
tags: [DetectionEngineering, IncidentResponse, SOC, DevSecOps, CyberSecurity]
source: "LinkedIn post P421 · DevSecOps series"
linkedin_date: 2029-06-05
design: reveal
---

# Detection and response terms, decoded

Six terms come up in every incident review, and two of them are usually being defined differently by the people in the room. Definitions are the contract.

## Quick reference

- **MTTD** — Mean time to detect: from the first event to the alert, averaged over incidents.
- **MTTR** — Mean time to resolve: from the alert to the service restored, averaged over incidents.
- **SIEM** — Security information and event management: it collects logs, runs rules and queues the alerts.
- **SOAR** — Security orchestration, automation and response: runbooks that enrich and act without a human.
- **IOC** — Indicator of compromise: a hash, an IP or a domain seen in an attack; useful, never proof.
- **Containment** — Stop the spread first: revoke the credential, isolate the host, then investigate.

## Explained

### The metrics

MTTD, mean time to detect, runs from the first event to the alert. It is the metric the attacker influences most, and it depends on log latency, rule windows and retention.

MTTR, mean time to resolve, runs from the alert to the service restored. Some teams use it for respond, so the definition goes in the report header.

### The platform

SIEM, security information and event management. It collects logs, normalises the fields, runs the rules and queues the alerts. The queue is the product, and retention is the bill.

SOAR, security orchestration, automation and response. Runbooks that enrich an alert, check a reputation feed and revoke a credential without a human. It is only as good as its last review.

### The incident

IOC, indicator of compromise: a hash, an IP or a domain seen in an attack. Matching one is a lead, never proof, because a good attacker rotates them.

Containment: stop the spread first. Revoke the credential, isolate the host, block the address, then investigate. Eradication comes after, not instead.

> **The honest caveat:** every number here can be gamed. Closing an incident early improves MTTR, and a narrow MTTD definition flatters the detection team.

> **The lesson:** define the stop clock before an incident.

That is the series. Fifty posts, from a threat model to a contained host, five phases and seven Python scripts. Thank you for following along.

## In one line

> **Detection is a programme, not a tool.** Fifty posts, one idea: the alert is the start of the work.

**Name the metric**

```bash
grep -i 'mttd' incident.md
```
