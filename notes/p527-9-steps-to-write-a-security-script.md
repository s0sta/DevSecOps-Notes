---
id: p527
title: "9 steps to write a security script"
slug: 9-steps-to-write-a-security-script
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, Automation, CICD, CyberSecurity]
source: "LinkedIn post P527 · PythonSec series"
linkedin_date: 2030-02-07
design: steps
---

# 9 steps to write a security script

A security script starts as a hunch: something in this file is wrong. Nine steps turn the hunch into a check that fails for the right reason and passes on a clean host. The terminal shows the interface first: usage, one run, one finding.

## Quick reference

### Spec — Decide what the check decides

```bash
# Write the help text first; it fixes the interface.
python3 audit.py --help
# One dirty fixture, smaller than the real file.
printf 'root ALL=(ALL) ALL\n' > /tmp/f
# Read the real line shape before the parser.
grep -n 'NOPASSWD' /tmp/f
```

### Build — Make the smallest correct pass

```bash
# Compile after every change; syntax is not a test.
python3 -m py_compile audit.py
# Run on the dirty fixture until exit 1 is stable.
python3 audit.py /tmp/f
# Then the clean one; it must exit 0 and print OK.
python3 audit.py /tmp/clean
```

### Prove — Prove the failure paths

```bash
# Missing input must print 2, not a traceback.
python3 audit.py /tmp/missing; echo $?
# stdout is the report; the exit code is the result.
python3 audit.py /tmp/f >/dev/null; echo $?
# Run it the way production will run it.
crontab -l | python3 audit.py -
```

## Explained

### Spec

`python3 audit.py --help` comes first. Write the help text before the code, because it fixes the input, the flags and the exit codes. `printf 'root ALL=(ALL) ALL\n' > /tmp/f` builds one dirty fixture, smaller than production and safe to break. `grep -n 'NOPASSWD' /tmp/f` reads the real line shape before a parser assumes it.

### Build

`python3 -m py_compile audit.py` catches syntax, not logic, so run it after every change. `python3 audit.py /tmp/f` runs on the dirty fixture until exit 1 is stable. `python3 audit.py /tmp/clean` then proves the clean path: exit 0 and one OK line. The two exits tell CI everything it needs.

### Prove

`python3 audit.py /tmp/missing; echo $?` must print 2, not a traceback. `python3 audit.py /tmp/f >/dev/null; echo $?` separates the report from the result, which is how CI reads it. `crontab -l | python3 audit.py -` runs it the way production will, through stdin.

> **The honest caveat:** a fixture you wrote will agree with a parser you wrote. Add one real, redacted file from production before you trust the pass.

> **The lesson:** a security script is a test, so write the assertion before the scanner.

## In one line

> **Write the check, then the fix.** A security script is a test with a docstring and an exit code.

**Start with --help**

```bash
python3 audit.py --help
```
