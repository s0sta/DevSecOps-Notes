---
id: p372
title: "The secure SDLC, drawn"
slug: the-secure-sdlc-drawn
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [DevSecOps, SecureSDLC, AppSec, CyberSecurity, CloudNative]
source: "LinkedIn post P372 · DevSecOps series"
linkedin_date: 2029-02-11
design: architecture
---

# The secure SDLC, drawn

Most teams can draw their build pipeline. Far fewer can point to the three places where security work actually happens, or name the person who owns each one.

## Quick reference

- **Design:** Security requirement (REQ) · Threat model (TM)
- **Build:** Code review (CR) · SAST scan (SAST)
- **Run:** Monitoring (MON) · Incident response (IR)

**Request flow:** Threat model → Code review → SAST scan → Monitoring → Incident response → Security requirement → Code review; Code review → Monitoring

## Explained

**Design**  
A security requirement turns a policy into something a pull request can satisfy: no card data in logs, no admin route without MFA. The threat model asks what can go wrong before code exists, so the fix costs a sentence instead of a sprint.

**Build**  
Code review looks for the flaw the author cannot see, and SAST scans every commit for the patterns a reviewer misses at 5 p.m. Neither replaces the other: the scanner has no runtime context, and the reviewer has no stamina.

**Run**  
Monitoring watches for the behaviour the first two tiers predicted: a spike in 401s, a new outbound host, a query that reads too much. Incident response is the tier with a name and a phone number at 3 a.m.

**The loop**  
The arrow back from response to design is what makes this a loop rather than a list. Every incident should end as a new requirement or a new test.

> **The honest caveat:** a three-tier diagram is not a control. If nobody owns the gate, each tier becomes a meeting that approves the last one.

> **The lesson:** security is a path through the SDLC, and every tier needs an owner, an artefact and an exit condition.

## In one line

> **Secure the path, not the stage.** A gate that nobody owns is a poster on a wall.

**Run the scan**

```bash
semgrep --config auto .
```
