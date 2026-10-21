---
id: p741
title: "Quiz: 3 exposure questions"
slug: quiz-3-exposure-questions
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, AttackSurface, AppSec, IncidentResponse, CloudSecurity]
source: "LinkedIn post P741 · ASM series"
linkedin_date: 2031-06-22
design: quiz
---

# Quiz: 3 exposure questions

Three questions from this phase, each one a decision you make while the clock is running.

## Quick reference

**Q1. Why is a 200 on a login page worse than a 403?**

- a) The request reached the panel
- b) The login is already bypassed
- c) A 403 means the page is cached

> **Answer:** a) The request reached the panel. A 403 is a refusal, often from an edge or ACL. A 200 means the request reached the panel, so the exposure is real. It still does not prove a bypass.

**Q2. What does an anonymous bucket listing reveal?**

- a) Only the bucket name
- b) The account's IAM policy
- c) Object names, sizes and dates

> **Answer:** c) Object names, sizes and dates. ListBucket returns keys, sizes and last-modified dates. Names leak customer IDs, backups and internal paths, and every key is a URL if the object is also public.

**Q3. Why is a leaked key an incident, not a finding?**

- a) It costs money to rotate
- b) It may already be in use
- c) It expires automatically

> **Answer:** b) It may already be in use. A finding is a weakness to schedule; a live credential is access that may already be exercised. You cannot tell from the repo, so rotate first and read the logs.

## Explained

### Question one

A login page returns 200; the same path behind a WAF returns 403. Which is worse? The 200 means the request reached the panel, so the exposure is real. The 403 is a refusal, often from something in front. Neither proves the login is bypassed, but the 200 is the one you can test.

### Question two

A bucket lists anonymously. What did you just leak? Object names, sizes and last-modified dates. Names carry customer IDs, backup schedules and internal paths, and every listed object is a URL if it is also public. The listing is the map; the objects are the data.

### Question three

A key is found in a bundle. Why is that an incident and not a finding? A finding is a weakness you can schedule. A live credential is access that may already be in use. You cannot tell from the repository whether it was exercised, so you rotate first and read the logs second.

> **The honest caveat:** the first two answers are about exposure, not impact. A reachable panel with MFA and a listing with no sensitive keys are still findings, but the response is a ticket, not a page.

> **The lesson:** a finding is a weakness; an incident is access.

## In one line

> **A key is access, not a finding.** Exposure is what answered; impact is what it can reach.

**Check the key**

```bash
aws iam list-access-keys --user-name app
```
