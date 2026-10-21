---
id: p547
title: "5 scripting mistakes in cloud audits"
slug: 5-scripting-mistakes-in-cloud-audits
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [DevSecOps, Python, CloudSecurity, Automation, CICD]
source: "LinkedIn post P547 · PythonSec series"
linkedin_date: 2030-03-26
design: dontdo
---

# 5 scripting mistakes in cloud audits

The audit script prints a beautiful table, the pipeline stays green, and the finding sits in a log nobody opens. The report was never the problem; the exit code was.

## Quick reference

**1.** ❌ **Hard-code the access key** — The script works, then the key leaks in a repo or a log.  
✅ **Use a short-lived role** — OIDC or a role gives the job credentials it cannot keep.

**2.** ❌ **Read only the first page** — A 1000-item API answers 1000 items; page two is invisible.  
✅ **Follow NextToken to the end** — Loop until the token is empty, then count what you saw.

**3.** ❌ **Missing key means clean** — A renamed field or a denied call turns unknown into green.  
✅ **Missing key means unknown** — Fail, or report it separately; never count it as checked.

**4.** ❌ **Print the whole response** — Tokens and emails land in CI logs kept for months.  
✅ **Mask values, print a hash** — Show AKIA... or a digest; never the secret itself.

**5.** ❌ **Print findings, exit 0** — The pipeline is green and the finding is a diary entry.  
✅ **Exit 1 on a finding** — CI reads the exit code, not the report body.

## Explained

### The five

Credentials. Hard-coding an access key makes the script work and the key leak. Use a role or OIDC, and let the job keep nothing.

Pagination. One call returns one page. Follow NextToken until it is empty, or the account you audit is only the first thousand resources.

Missing data. A renamed field or a denied call is not a pass. Treat absent data as unknown, and count it separately from checked.

Secrets in output. Printing the whole response copies tokens and emails into CI logs. Mask the value; show a prefix or a hash.

Exit code. Print findings and exit 0, and CI has nothing to act on. Exit 1 on a finding, 2 on an error, 0 only when clean.

### What they share

Each one makes the script feel finished while leaving the decision to a human who never sees it. None of the five looks wrong on the day it is written.

> **The honest caveat:** a non-zero exit is a blunt instrument. One low finding fails the build until someone allowlists it. That friction is the point, but keep the allowlist reviewed.

> **The lesson:** make the check fail, or it is not a check.

## In one line

> **A report is not a gate.** If the check cannot fail, it is a newsletter.

**Return 1**

```bash
sys.exit(1 if bad else 0)
```
