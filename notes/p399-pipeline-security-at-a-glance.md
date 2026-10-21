---
id: p399
title: "Pipeline security at a glance"
slug: pipeline-security-at-a-glance
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevSecOps, CICD, Metrics, CyberSecurity, CloudNative]
source: "LinkedIn post P399 · DevSecOps series"
linkedin_date: 2029-04-15
design: dashboard
---

# Pipeline security at a glance

A security board that nobody owns is a wall decoration. These six tiles are the ones a pipeline team can change this sprint, each with a name and a number.

## Quick reference

**Status:** Last 30 days

| Metric | Value | Note |
|:--|:--|:--|
| Unsigned images | **7** | of 42 in production |
| Unpinned actions | **23** | of 61 use sites |
| Failed scans | **3** | blocked the merge |
| Secret hits | **1** | revoked in 11 minutes |
| OIDC jobs | **90%%** | no stored cloud key |
| Mean fix time | **2.4d** | critical: 1.1 days |

## Explained

### Coverage

Unsigned images. Seven of forty-two images in production have no signature. Count them by listing the running digests and checking each against the cosign transparency log; an image built outside the pipeline is the usual gap.

Unpinned actions. Twenty-three of sixty-one uses: references point at a tag, not a SHA. The count is mechanical: every uses: line that does not end in a 40-character ref.

Failed scans. Three scans failed in the last thirty days and blocked the merge. A scan that fails without blocking is a dashboard, not a gate.

### Exposure

Secret hits. One credential was found in a workflow log and revoked in eleven minutes. The number that matters is the time from exposure to revocation, not the count.

OIDC jobs. Ninety per cent of jobs get cloud credentials through OIDC, with no stored key. The remaining ten per cent are the ones to migrate first.

### Response

Mean fix time. 2.4 days from finding to merge, and 1.1 days for critical findings. Track the tail, not the mean.

> **The honest caveat:** every tile is only as good as its coverage; the unsigned tile counts what the registry knows, and mean fix time hides the one finding that has been open for a year.

> **The lesson:** six numbers, six owners, one review every Monday.

## In one line

> **A board is not a control.** Six numbers, six owners, one review every Monday.

**Count the pins**

```bash
grep -rn 'uses:' .github/ | wc -l
```
