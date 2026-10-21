---
id: p524
title: "Four rules for safe automation"
slug: four-rules-for-safe-automation
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, Automation, CICD, CyberSecurity]
source: "LinkedIn post P524 · PythonSec series"
linkedin_date: 2030-01-31
design: explainer
---

# Four rules for safe automation

A script that edits `/etc` while it audits `/etc` is not an audit. It is a change with a report attached. Four rules keep the difference obvious.

## Quick reference

### Read-only first

- Open files with mode r, never w
- No shell=True, no eval, no exec
- A `--dry-run` path is the default

### Exit codes are the API

- 0 clean, 1 finding, 2 usage
- Never exit 0 after a failed check
- CI reads the code, not the prose

### Idempotent by design

- Run twice, get the same report
- No append without a dedupe key
- State stays outside the script

### Log to stderr

- stdout is the report, stderr the noise
- One finding per line, same prefix
- Mask values, never echo a secret

## Explained

### Read-only first

Open every file with mode r, never w. No shell=True, no eval, no exec: each turns data into code. A `--dry-run` path should be the default, with writes behind a flag someone has to type on purpose.

### Exit codes are the API

0 clean, 1 finding, 2 usage or unreadable input. A check that fails must never exit 0, or CI will believe it. The code is the contract; the prose is for the human who reads it afterwards.

### Idempotent by design

Run it twice and the report should match. Do not append without a dedupe key, and keep state outside the script: a lock file, a database, a ticket. The script becomes a function you can call again.

### Log to stderr

stdout is the report, stderr is the noise. One finding per line, same prefix, so grep and a parser agree. Mask values, never echo a secret, even when it is the thing that broke.

> **The honest caveat:** read-only is a property of every code path, not a comment at the top. One subprocess call can undo it.

> **The lesson:** the safest automation is the one you can run twice, on production, without asking.

## In one line

> **Read-only, predictable, quiet.** The rules are boring; the incident they prevent is not.

**Dry run first**

```bash
python3 audit.py --dry-run
```
