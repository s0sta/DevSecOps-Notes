---
id: p565
title: "A log redactor in Python"
slug: a-log-redactor-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, Logging, Security, DevSecOps, SRE]
source: "LinkedIn post P565 · PythonSec series"
linkedin_date: 2030-05-07
design: code
script: log_redact.py
---

# A log redactor in Python

A production log carries email addresses, client IPs and the occasional bearer token, and log shipping copies all of it to three systems with weaker access. Redaction is the step between the file and the archive.

## Quick reference

The full script is at the end of this note: `log_redact.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 log_redact.py app.log
```

**Example output**

```text
2026-10-21T09:14:02Z api login [EMAIL] from [IP]
2026-10-21T09:14:03Z api auth Bearer [TOKEN]
```

## Explained

### What it does

The script reads log lines from a file or stdin and applies four patterns in order: email, IPv4, bearer token, long hex. Email and IPv4 come first because they are easy to over-match. The bearer pattern keeps the scheme and masks the value. Hex last catches commit SHAs and keys of 32 characters or more.

### The run

`python3 log_redact.py app.log` prints the same lines with the address as [EMAIL], the client as [IP] and the credential as Bearer [TOKEN]. A long hex run becomes [HEX] the same way. It writes only to stdout, so redirect it or pipe it into the next tool. A redaction is the job, so a file with hits still exits 0; exit 2 means the file or the input was unreadable.

### Why the order

A JWT can carry a hex run inside it. A hex regex run first would cut the token into pieces and leave the rest exposed, so the token pattern has to run first.

> **The honest caveat:** these patterns miss a secret split across lines, encoded in a blob or written in an unfamiliar format. A redacted log is safer, not safe.

> **The lesson:** redact before the log travels, not after it leaks.

## In one line

> **Redact the line, keep the evidence.** A log is evidence, so mask it before it travels.

**Mask before ship**

```bash
python3 log_redact.py app.log > safe.log
```

## Script: log_redact.py

Download: [scripts/log_redact.py](../scripts/log_redact.py)

```python
#!/usr/bin/env python3
"""log_redact.py - redact secrets and identifiers from log lines.

Reads log text from files or stdin, masks email addresses, IPv4 addresses,
bearer tokens and long hexadecimal strings, and writes the result to stdout.
The input files are never modified.

    EMAIL    [EMAIL]        anything shaped like user@example.com
    IPv4     [IP]           10.0.0.7, 192.168.1.20
    TOKEN    Bearer [TOKEN] the credential after a Bearer scheme
    HEX      [HEX]          32 or more hexadecimal characters

Usage:
    python3 log_redact.py app.log
    cat app.log | python3 log_redact.py
    journalctl -u api --since -1h | python3 log_redact.py > safe.log
    python3 log_redact.py access.log error.log
    python3 log_redact.py --help

CI (sanitise an artefact before upload):
    python3 log_redact.py build.log > build.redacted.log || exit 2

Cron (a daily archive of one service log):
    15 2 * * * journalctl -u api --since -1d | python3 /opt/s0sta/log_redact.py >> /var/log/api.redacted

Exit codes: 0 input read and redacted, 2 usage or unreadable input.
A redaction is the job, not a failure, so a file with hits still exits 0.

Read-only: it writes nothing except stdout and opens no network socket.

The patterns are deliberately narrow. They catch the common shapes and miss
secrets split across lines, encoded blobs and credentials in other formats.
A redacted log is safer, not safe.

By s0sta.com
"""
import argparse
import re
import sys

PATTERNS = (
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP]"),
    (re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/-]+=*"), r"\1[TOKEN]"),
    (re.compile(r"\b[0-9A-Fa-f]{32,}\b"), "[HEX]"),
)


def redact(line):
    """Return one line with every known shape replaced."""
    for pattern, replacement in PATTERNS:
        line = pattern.sub(replacement, line)
    return line


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Redact emails, IPv4 addresses, bearer tokens and long "
                    "hex strings from log lines.")
    parser.add_argument("files", nargs="*", metavar="FILE",
                        help="log files; read stdin when none is given")
    args = parser.parse_args(argv)
    for name in args.files or ["-"]:
        try:
            if name == "-":
                for line in sys.stdin:
                    sys.stdout.write(redact(line))
            else:
                with open(name, "r", encoding="utf-8") as handle:
                    for line in handle:
                        sys.stdout.write(redact(line))
        except (OSError, UnicodeError) as exc:
            print("log_redact: %s: %s" % (name, exc), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
