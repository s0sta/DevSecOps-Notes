---
id: p771
title: "Quiz: 3 proof questions"
slug: quiz-3-proof-questions
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [Python, VulnerabilityManagement, CyberSecurity, GRC, DevSecOps]
source: "LinkedIn post P771 · ASM series"
linkedin_date: 2031-08-31
design: quiz
---

# Quiz: 3 proof questions

The series ends with three questions, and each one is about proof that survives a review. Answer before the reveal.

## Quick reference

**Q1. Why does a closure rate need a denominator?**

- a) Because closed counts are always wrong
- b) Because a rate is a ratio of two counts
- c) Because auditors ask for a percentage

> **Answer:** b) Because a rate is a ratio of two counts. Closed divided by findings in play, open at the start plus opened, gives a rate you can compare. Without it, a team closes more while the backlog grows.

**Q2. What must a coverage report include to be true?**

- a) Inventory, required tools and a time window
- b) The number of scans the scanner sent
- c) Every asset the scanner already knows

> **Answer:** a) Inventory, required tools and a time window. Coverage is a join against the inventory, tool by tool, in a window. Scans over known assets measure the scanner, and an asset outside the inventory is invisible.

**Q3. Why does a control need dated evidence?**

- a) Evidence makes the report longer
- b) The framework requires a screenshot
- c) A policy is intent; a file is fact

> **Answer:** c) A policy is intent; a file is fact. A dated file and a hash let someone who was not there check the control. Without them, enabled is a belief, and a disabled control can survive a quarter of reviews.

## Explained

### Question one

Why does a closure rate need a denominator? Because a rate is a ratio, and 48% means nothing until you name the bottom. Closed divided by the findings in play, open at the start plus opened during the period, gives a number you can compare across months. Without it, a team can close more findings every quarter while the backlog grows.

### Question two

What must coverage include? The inventory, the required tools and the time window. Scans sent divided by assets the scanner knew about is not coverage; an asset missing from the inventory is invisible. A clean report that omits a critical database is a report about the scanner, not the estate.

### Question three

Why does a control need evidence? Because a policy states intent and an export states fact. A dated file and a hash make the control checkable by someone who was not there. Without them, "enabled" is a belief, and a disabled control can survive a quarter of reviews.

> **The honest caveat:** passing this quiz does not make the programme provable; the schedule, the owners and the evidence do.

> **The lesson:** measure it, map it, prove it.

That is the series. Fifty posts, five phases and twenty-five Python scripts, from the first certificate to this packet. Thank you for following along.

## In one line

> **Measure it, map it, prove it.** Fifty posts, five phases, twenty-five scripts, one proof chain.

**Keep the proof**

```bash
python3 audit_packet.py ev -f f -s s -r r
```
