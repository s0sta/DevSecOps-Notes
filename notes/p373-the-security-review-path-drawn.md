---
id: p373
title: "The security review path, drawn"
slug: the-security-review-path-drawn
sections: [devsecops]
topic: "Application & API security"
tags: [DevSecOps, AppSec, ThreatModelling, CyberSecurity, SecureSDLC]
source: "LinkedIn post P373 · DevSecOps series"
linkedin_date: 2029-02-13
design: architecture
---

# The security review path, drawn

A feature request arrives with a deadline already attached. Security gets two days to comment, and the comment is a list of worries with no owner and no date.

## Quick reference

- **Request:** Feature request (REQ) · Data flow (DFD)
- **Review:** Threat model (TM) · Design review (DR)
- **Decision:** Accept (ACC) · Mitigate (MIT) · Block (BLK)

**Request flow:** Feature request → Threat model → Design review → Accept; Design review → Mitigate; Design review → Block; Data flow → Threat model; Data flow → Design review

## Explained

**Request**  
A feature request and a data flow diagram are the entry ticket. The diagram does not need to be beautiful; it needs to show every place data crosses a trust boundary and which identity carries it.

**Review**  
The threat model turns that diagram into named risks. The design review checks the answers: is the token validated, is the tenant check on every query, what happens when the queue is replayed. Both happen before code, where a change costs a sentence.

**Decision**  
The decision tier has three exits. Accept records the risk, the owner and the date it is reviewed again. Mitigate names the control and the test that proves it. Block stops the work and says what would unblock it.

**Why it stalls**  
Most review processes have the first two tiers and no third, so the same risks return every quarter with better slides.

> **The honest caveat:** the diagram is a model, not the system. If it is drawn once and never updated, the review is theatre with a colour scheme, and nobody can point to the decision.

> **The lesson:** a review is finished when someone with authority writes down a decision, not when the comments are resolved.

## In one line

> **No decision, no review.** A review that ends in 'looks fine' has not ended.

**Ask for a decision:** accept, mitigate or block?
