---
id: p605
title: "A CI log secret leak scan"
slug: a-ci-log-secret-leak-scan
sections: [devsecops]
topic: "Python scripts"
tags: [DevSecOps, CICD, Security, Python, Secrets]
source: "LinkedIn post P605 · PythonFixes series"
linkedin_date: 2030-08-08
design: code
script: ci_log_leak.py
---

# A CI log secret leak scan

A debug line prints the deploy role's access key, the job passes, and the log is retained for ninety days where every engineer can read it.

## Quick reference

The full script is at the end of this note: `ci_log_leak.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 ci_log_leak.py /tmp/run.log
```

**Example output**

```text
LEAK 3 aws-key ****************
LEAK 5 bearer ****************
```

## Explained

### What it does

`ci_log_leak.py` reads one log file or stdin and checks each line for the shapes that leak most often: AWS keys, GitHub and GitLab tokens, Slack tokens, private key headers, Bearer tokens and generic api_key, secret, token or password assignments. Each hit prints the line number, the kind and sixteen asterisks; the run exits 1 without printing the value.

### What the screen shows

The fourteen lines load the log, define four patterns, then walk the lines and stop at the first match on each. The print line writes LEAK, the line number, the kind and the mask; break keeps one finding per line. On the dirty log the two lines are LEAK 3 aws-key and LEAK 5 bearer, each with the same fixed mask.

### How to run it

`python3 ci_log_leak.py build.log`, or pipe a job log through stdin. Put it before the upload step, so a leak fails the job instead of reaching the archive.

### The fix

Revoke and rotate the credential first, then remove the line and purge the log.

### Prevention

Keep secret masking on, never run `set -x` around a token, and scan every saved log before upload. Masking hides exact strings; a base64 copy can still print.

> **The honest caveat:** pattern matching misses split, encoded and unusual secrets. A clean scan is not proof of a clean log.

> **The lesson:** treat the CI log as a public artefact, because it usually is.

## In one line

> **A green log can still leak.** The build passed; the credential is now in the archive.

**Scan one log**

```bash
python3 ci_log_leak.py build.log
```

## Script: ci_log_leak.py

Download: [scripts/ci_log_leak.py](../scripts/ci_log_leak.py)

```python
#!/usr/bin/env python3
"""Scan a CI log for likely secrets without printing the secret.

Reads one log file (or stdin), checks each line against the shapes that leak
most often in build output, and prints one masked line per hit:

    LEAK 12 aws-access-key ****************
    LEAK 40 bearer ****************

The value is never printed, not even a prefix: a short prefix is still a
secret. The line number and the kind are enough to find the line and rotate
the credential.

Patterns: AWS access key IDs (AKIA/ASIA), AWS secret access keys, GitHub and
GitLab tokens, Slack tokens, private key headers, Bearer tokens and generic
api_key/secret/token/password assignments. The match is only the trigger; the
line text is discarded.

Usage:
    python3 ci_log_leak.py build.log
    cat build.log | python3 ci_log_leak.py
    gh run view 123456 --log > /tmp/run.log
    python3 ci_log_leak.py /tmp/run.log

Exit codes: 0 no likely secret, 1 at least one finding, 2 usage or an
unreadable input.

CI (scan a saved job log before it is uploaded):
    python3 ci_log_leak.py build.log || exit 1

Cron (scan yesterday's deploy log):
    15 5 * * * python3 /opt/s0sta/ci_log_leak.py /var/log/deploy.log

The scan is read-only and opens no network socket. It is pattern matching,
not proof: a secret split across lines, base64-encoded, or written by a tool
in another format is missed. GitHub and GitLab mask exact values in the live
log, but a transformed value or a debug dump can still print. Revoke first,
then remove the line; deleting the log does not un-leak the credential.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import re
import sys

MASK = "*" * 16

PATTERNS = (
    ("aws-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("aws-secret-key", re.compile(
        r"(?i)aws_?secret_?access_?key\s*[:=]\s*[\"']?[A-Za-z0-9/+=]{40}")),
    ("private-key", re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY(?: BLOCK)?-----")),
    ("github-token", re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,})\b")),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*")),
    ("assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*"
        r"[\"']?[A-Za-z0-9_\-./+=]{12,}")),
)


def scan_line(line):
    """Return the kind of the first matching pattern, or None."""
    for kind, pattern in PATTERNS:
        if pattern.search(line):
            return kind
    return None


def read_lines(source):
    """Return the lines of a log file or stdin, or raise OSError."""
    if source == "-":
        return sys.stdin.readlines()
    with open(source, "r", encoding="utf-8", errors="replace") as handle:
        return handle.readlines()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Find likely secrets in a CI log and print the line "
                    "number with a masked value, never the value.",
        epilog="Exit codes: 0 clean, 1 findings, 2 usage or input error.")
    parser.add_argument("log", nargs="?", default="-",
                        help="log file, or - for stdin (default)")
    args = parser.parse_args(argv)

    try:
        lines = read_lines(args.log)
    except (OSError, UnicodeError) as exc:
        print("ERR cannot read %s: %s" % (args.log, exc), file=sys.stderr)
        return 2

    hits = []
    for number, line in enumerate(lines, 1):
        kind = scan_line(line)
        if kind is not None:
            hits.append((number, kind))
    if not hits:
        print("OK no likely secrets in %d lines" % len(lines))
        return 0
    print("SCAN %d lines, %d findings" % (len(lines), len(hits)))
    for number, kind in hits:
        print("LEAK %d %s %s" % (number, kind, MASK))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
