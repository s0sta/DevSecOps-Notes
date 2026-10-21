---
id: p571
title: "Quiz: 3 reporting questions"
slug: quiz-3-reporting-questions
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, SecurityReporting, Automation, CICD]
source: "LinkedIn post P571 · PythonSec series"
linkedin_date: 2030-05-21
design: quiz
---

# Quiz: 3 reporting questions

Three questions close the series, and each one is a decision you make when you publish a report.

## Quick reference

**Q1. Why does a report need an exit code?**

- a) So the pipeline can fail on a finding
- b) So the report can be signed
- c) So the log stays short

> **Answer:** a) So the pipeline can fail on a finding. The exit code is the one machine-readable verdict. 0, 1 and 2 let CI gate without parsing prose, and the number survives every log format.

**Q2. Why is a false positive a product bug?**

- a) It spends the reviewer's trust
- b) It proves the scanner is broken
- c) It lowers the average severity

> **Answer:** a) It spends the reviewer's trust. Every false positive costs attention and teaches people to ignore the next alert. The product is a decision, and a wrong one is a defect, not a rounding error.

**Q3. What makes a finding reproducible?**

- a) A command, a version and a fixture
- b) A screenshot and a summary
- c) A severity and an owner

> **Answer:** a) A command, a version and a fixture. Someone else can run the same command on the same version with the same input and get the same result. Without that, it is an anecdote, not a finding.

## Explained

### Question one

Why does a report need an exit code? Because the exit code is the one machine-readable verdict. 0, 1 and 2 let CI gate without parsing prose, and the number survives every log format and every reader.

### Question two

Why is a false positive a product bug? Because every false positive spends a reviewer's attention and teaches people to ignore the next alert. The scanner's product is a decision, and a wrong one is a defect, not a rounding error. A report that cries wolf once is a report people stop reading.

### Question three

What makes a finding reproducible? A command, a version and a fixture. Someone else can run the same command on the same version with the same input and get the same result. Without that, it is an anecdote, not a finding.

> **The honest caveat:** passing this quiz does not make a report true. The evidence does, and the evidence is the part you have to go and collect.

> **The lesson:** a report is finished when someone can act on it.

That is the series. Fifty posts, from the first sshd check to a report a pipeline can read, five phases and twenty Python scripts. Thank you for following along.

## In one line

> **Report it, then gate it.** Fifty posts end where the work starts: a report someone can act on.

**Start with one**

```bash
python3 log_redact.py app.log
```
