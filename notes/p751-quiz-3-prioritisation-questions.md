---
id: p751
title: "Quiz: 3 prioritisation questions"
slug: quiz-3-prioritisation-questions
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, EPSS, CISAKEV, CyberSecurity, AppSec]
source: "LinkedIn post P751 · ASM series"
linkedin_date: 2031-07-15
design: quiz
---

# Quiz: 3 prioritisation questions

Three questions separate a number from a decision. Answer before the reveal.

## Quick reference

**Q1. EPSS reports 0.71 for a CVE. What does that number mean?**

- a) 71% chance of exploitation in 30 days
- b) A severity score of 7.1 out of 10
- c) 71% of your assets are exposed

> **Answer:** a) 71% chance of exploitation in 30 days. EPSS is a probability between 0 and 1, estimated for the next 30 days. It says nothing about severity or about your estate, and 0.71 is not 7.1.

**Q2. What does a KEV listing add that EPSS cannot?**

- a) A probability of exploitation
- b) Evidence it was exploited in the wild
- c) A CVSS base score

> **Answer:** b) Evidence it was exploited in the wild. KEV records vulnerabilities with evidence of exploitation, plus a due date. It is a fact about the past, not a forecast, which is why it outranks a higher score.

**Q3. Why can reachability change the order of a queue?**

- a) It lowers the CVSS base score
- b) Unreachable code cannot be exploited now
- c) It proves the CVE is a false positive

> **Answer:** b) Unreachable code cannot be exploited now. A vulnerable package that no live path imports cannot run today. That is a reason to defer, not to close: the call path can appear in the next release.

## Explained

### Question one

EPSS reports 0.71 for a CVE. What does that mean? A 71% chance of exploitation in the next 30 days, not a severity of 7.1. EPSS is a probability between 0 and 1, estimated daily for the next 30 days from observed exploitation signals. It says nothing about impact, and nothing about your asset. Reading 0.71 as 7.1 is the most common mistake in the whole queue.

### Question two

What does a KEV listing add that EPSS cannot? Evidence. KEV records vulnerabilities with public evidence of exploitation in the wild, plus a remediation due date. EPSS is a forecast; KEV is a fact about the past. That is why a 6.5 in KEV outranks a 9.8 that has only a probability.

### Question three

Why can reachability change the order? Because unreachable code cannot run today. A package that no live path imports is a reason to defer, not to close: the call path can reappear with the next release. Static analysis gives you the argument, not a proof.

> **The honest caveat:** none of the three decides alone, and all three can be wrong on a given Tuesday.

> **The lesson:** a probability, a record and a path are three different claims, and a priority is what you do when they disagree.

## In one line

> **Know what each number means.** A probability, a record and a path are three different claims.

**Check your answer**

```bash
python3 epss_rank.py f.json e.csv
```
