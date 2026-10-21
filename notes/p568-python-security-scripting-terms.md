---
id: p568
title: "Python security scripting terms"
slug: python-security-scripting-terms
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, SecurityAutomation, CICD, SRE]
source: "LinkedIn post P568 · PythonSec series"
linkedin_date: 2030-05-14
design: reveal
---

# Python security scripting terms

A script review can stall on a single word: someone says idempotent and two people in the room mean different things. Six terms cover most of the argument.

## Quick reference

- **idempotent** — Running it twice leaves the same state as running it once, so a retry is safe.
- **exit code** — 0 clean, 1 finding, 2 bad input: the number a pipeline reads instead of prose.
- **read-only** — It inspects and reports; it never writes the repo, the host or the network.
- **parser** — Code that turns text into fields you can test, instead of regex guesses on raw output.
- **fixture** — A small input with a known answer, kept beside the test so tomorrow runs the same.
- **gate** — A check whose exit code blocks a merge or a deploy, not a report nobody opens.

## Explained

### The terms

Idempotent: running it twice leaves the same state as running it once, so a retry is safe. If a second run creates a second ticket, the script is not idempotent.

Exit code: 0 clean, 1 finding, 2 bad input. The number is the interface a pipeline reads; the prose is for the human who arrives later.

Read-only: it inspects and reports, and never writes the repo, the host or the network. A read-only script can run against production without a change window.

Parser: code that turns text into fields you can test, instead of regex guesses on raw output. A parser makes the check explainable when it fires.

Fixture: a small input file with a known answer, kept beside the test. Without one, a change to the script has nothing to disagree with.

Gate: a check whose exit code blocks a merge or a deploy, not a report nobody opens. A gate is a control; a report is a hope.

### The contract

> **The honest caveat:** a script can be idempotent, read-only and gated and still check the wrong thing. The terms describe the contract, not the correctness.

> **The lesson:** a script is a contract of input, output and exit code.

## In one line

> **A script is a contract.** Input, output, exit code: the three things a reviewer checks first.

**Read the docstring**

```bash
python3 script.py --help
```
