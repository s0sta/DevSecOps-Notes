---
id: p531
title: "Quiz: 3 automation questions"
slug: quiz-3-automation-questions
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, Automation, CyberSecurity, CICD]
source: "LinkedIn post P531 · PythonSec series"
linkedin_date: 2030-02-17
design: quiz
---

# Quiz: 3 automation questions

Three questions come back in every review of an automation script, and the answers separate a tool from a liability.

## Quick reference

**Q1. Why exit 2 instead of 1 when the input is unreadable?**

- a) 2 means the check itself failed
- b) 2 is the standard for a finding
- c) 1 is reserved for syntax errors

> **Answer:** a) 2 means the check itself failed. 1 means the check ran and found something. 2 means it could not run. CI can separate a finding from a broken scanner, and a broken scanner is not a clean host.

**Q2. Why is shell=True a vulnerability in a scanner?**

- a) It is slower than an argument list
- b) It passes data through `/bin/sh`
- c) It hides the exit code

> **Answer:** b) It passes data through `/bin/sh`. A list keeps every argument a value. With shell=True the joined string is parsed again, so a filename or a log line containing a semicolon becomes a command.

**Q3. Why must a scanner be read-only?**

- a) So it can run on production safely
- b) Because writes are slower
- c) Because cron runs as root

> **Answer:** a) So it can run on production safely. A read-only check is safe to repeat on a live host and its result is reproducible. The moment it edits state, the check becomes a change with a rollback problem.

## Explained

### Exit 2

Question one: why exit 2 instead of 1 when the input is unreadable? 1 means the check ran and found something. 2 means it could not run. CI can then tell a finding from a broken scanner, and a broken scanner is not a clean host. If a missing file exits 1, the pipeline reports a vulnerability that does not exist.

shell=True

Question two: why is shell=True a vulnerability in a scanner? A list keeps every argument a value. With shell=True the joined string is parsed again by `/bin/sh`, so a filename or a log line containing a semicolon or a dollar sign becomes syntax. The scanner reads untrusted text all day, which is exactly the input you must not hand to a shell.

### Read-only

Question three: why must a scanner be read-only? A check should be safe to repeat on production, and its result reproducible. The moment it edits state, it becomes a change with a rollback problem. Read-only is not a limitation; it is what lets you run the tool at 3 a.m.

> **The honest caveat:** read-only is not passive. A scanner can still exhaust CPU, fill a log or hold a lock, so give it a timeout and a budget.

> **The lesson:** the exit code and the write path are part of the security review.

## In one line

> **The code is the contract.** Three answers that decide whether the report can be trusted.

**Check the exit**

```bash
python3 audit.py; echo $?
```
