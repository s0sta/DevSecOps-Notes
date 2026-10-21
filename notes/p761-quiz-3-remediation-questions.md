---
id: p761
title: "Quiz: 3 remediation questions"
slug: quiz-3-remediation-questions
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, CyberSecurity, Python, DevOps, SRE]
source: "LinkedIn post P761 · ASM series"
linkedin_date: 2031-08-07
design: quiz
---

# Quiz: 3 remediation questions

Three questions come back in every remediation review. Answer before the reveal.

## Quick reference

**Q1. Why must a patch wave be small?**

- a) A change window can review only so much
- b) Small waves fix more findings
- c) Large waves need more scanners

> **Answer:** a) A change window can review only so much. A wave is a change request. If the board cannot read every item, it approves the plan without reading it, and one bad patch rolls back the whole batch.

**Q2. What must a risk exception carry?**

- a) An owner, a reason and an expiry
- b) A CVSS score and a ticket
- c) A vendor contact and a date

> **Answer:** a) An owner, a reason and an expiry. Without an owner nobody acts, without a reason nobody can judge it, and without an expiry it never returns. The date turns an acceptance into a decision.

**Q3. Why is a rescan the only closure proof?**

- a) It runs the same checks and shows the delta
- b) It proves the patch command exited 0
- c) It lists the findings that were fixed

> **Answer:** a) It runs the same checks and shows the delta. A patch command proves an install ran, not that the finding is gone. A rescan with the same checks shows it absent, and catches the check someone disabled.

## Explained

### Question one

Why must a patch wave be small? Because a wave is a change request, and a board that cannot read every item approves the plan without reading it. Nine critical patches in one window is not urgency, it is a batch rollback waiting to happen. Split by service, keep the owner attached, and let the next window carry the rest.

### Question two

What must a risk exception carry? An owner, a reason and an expiry. Without an owner nobody acts, without a reason nobody can judge the risk, and without an expiry it never comes back. The date turns an acceptance into a decision, and the register script fails the run when the date passes.

### Question three

Why is a rescan the only closure proof? Because a patch command proves that an install ran, not that the finding is gone. A rescan with the same checks shows the finding absent and no new one, and catches the check that someone disabled. Without the check list, a closed finding is a claim.

The three connect: a small wave ships, an exception with a date expires, and a rescan closes. Remove any one and the other two report progress without evidence.

> **The honest caveat:** passing this quiz does not fix a host; the window and the rescan do.

> **The lesson:** remediation is a loop, and the last step is the one that counts.

## In one line

> **Closing needs a second scan.** Three questions before the next closure.

**Diff the rescan**

```bash
python3 rescan_diff.py b.json a.json
```
