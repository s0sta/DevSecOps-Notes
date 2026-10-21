---
id: p555
title: "A CSP audit in Python"
slug: a-csp-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [CSP, WebSecurity, Python, DevSecOps, HTTP]
source: "LinkedIn post P555 · PythonSec series"
linkedin_date: 2030-04-14
design: code
script: csp_audit.py
---

# A CSP audit in Python

A Content-Security-Policy header arrives as one long string, and most reviews read the first directive and stop. A script can check every weak token in a second.

## Quick reference

The full script is at the end of this note: `csp_audit.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 csp_audit.py --headers /tmp/h.json
```

**Example output**

```text
FAIL 3 csp finding(s)
unsafe-inline; *; no frame-ancestors
```

## Explained

### What it checks

The script reads a headers JSON dump or a raw policy. It splits the semicolon-separated directives and keeps the effective script sources: script-src when present, default-src otherwise. It flags unsafe-inline, unsafe-eval, a bare \*, a missing default-src and a missing frame-ancestors. Directives are matched case-insensitively, and a policy spread over several headers is checked one header at a time.

### The run

On the sample dump it prints two lines: FAIL 3 csp finding(s), then unsafe-inline; \*; no frame-ancestors. Exit 1 makes it a gate, exit 0 is clean, and exit 2 means the file or the JSON is unreadable. The full script is attached, standard library only and read-only.

### The fix

Each label maps to a change. Replace unsafe-inline with a nonce or a hash, remove unsafe-eval and the library that needs it, replace \* with the hosts you actually use, add default-src 'self', and add frame-ancestors 'none'. A nonce has to be generated per response, not per deploy, or it becomes a new constant.

> **The honest caveat:** a strict policy can still allow a compromised script from an allowlisted host, and a report-only policy will not fail the gate. Read the reports before you enforce.

> **The lesson:** a policy is code, so test it like code.

## In one line

> **Read the policy, not the badge.** A header is only as good as the directives inside it.

**Audit the policy**

```bash
python3 csp_audit.py --headers h.json
```

## Script: csp_audit.py

Download: [scripts/csp_audit.py](../scripts/csp_audit.py)

```python
#!/usr/bin/env python3
"""Audit a Content-Security-Policy header for weak directives.

Reads a response-headers JSON dump, or a raw policy string, and flags:

    unsafe-inline        inline script runs without a nonce or hash
    unsafe-eval          string-to-code evaluation is allowed
    *                    any host may serve script
    no default-src       every unlisted fetch type falls back to defaults
    no frame-ancestors   any site may frame the page

The script checks the effective script sources: script-src when it exists,
default-src otherwise. A missing Content-Security-Policy header is reported
as a finding, because no policy is not the same as a strict policy. A
headers dump may be an object of names to values, an object with a "headers"
object, or a list of {"name": ..., "value": ...} entries; names are matched
case-insensitively.

Usage:
    python3 csp_audit.py --headers /tmp/headers.json
    python3 csp_audit.py --policy "default-src 'self'; script-src 'self'"
    python3 csp_audit.py --headers /tmp/headers.json --verbose
    python3 csp_audit.py --help

CI (after a deploy):
    python3 csp_audit.py --headers /tmp/headers.json || exit 1

Cron (daily at 06:00):
    0 6 * * * python3 /opt/s0sta/csp_audit.py --headers /var/tmp/h.json

Exit codes: 0 clean, 1 at least one finding, 2 usage or unreadable input.
Read-only: the file is read, nothing is written, nothing is fetched.

The honest limit: a policy can be strict and still allow an old bundled
library to run; this checks directives, not the code they load.

By s0sta.com
"""
import argparse
import json
import sys

HEADER = "content-security-policy"


def parse_policy(policy):
    """Return {directive: [sources]} for one policy string."""
    directives = {}
    for part in policy.split(";"):
        tokens = part.split()
        if not tokens:
            continue
        name = tokens[0].lower()
        directives.setdefault(name, []).extend(tokens[1:])
    return directives


def load_headers(path):
    """Return a lowercase {header: [values]} map from a JSON dump."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    except json.JSONDecodeError as exc:
        raise ValueError("%s is not valid JSON: %s" % (path, exc))

    if isinstance(data, dict) and isinstance(data.get("headers"), dict):
        data = data["headers"]

    if isinstance(data, dict):
        items = list(data.items())
    elif isinstance(data, list):
        items = []
        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError("each header entry must be an object")
            name = entry.get("name")
            if name is None:
                raise ValueError("a header entry has no name")
            items.append((name, entry.get("value", "")))
    else:
        raise ValueError("headers JSON must be an object or a list")

    headers = {}
    for name, value in items:
        key = str(name).lower()
        values = value if isinstance(value, list) else [value]
        clean = [str(item) for item in values if item is not None]
        if clean:
            headers.setdefault(key, []).extend(clean)
    return headers


def audit(policy):
    """Return a list of (label, detail) findings for one policy string."""
    directives = parse_policy(policy)
    script = directives.get("script-src", directives.get("default-src", []))
    lowered = [source.lower() for source in script]
    findings = []
    if "'unsafe-inline'" in lowered:
        findings.append(("unsafe-inline",
                         "the effective script sources allow inline code"))
    if "'unsafe-eval'" in lowered:
        findings.append(("unsafe-eval",
                         "the effective script sources allow eval"))
    if "*" in lowered:
        findings.append(("*", "the effective script sources allow any host"))
    if "default-src" not in directives:
        findings.append(("no default-src",
                         "unlisted fetch types use the browser defaults"))
    if "frame-ancestors" not in directives:
        findings.append(("no frame-ancestors",
                         "CSP does not restrict framing"))
    return findings


def build_parser():
    """Return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="csp_audit.py",
        description="Flag weak Content-Security-Policy directives in a "
                    "headers JSON dump or a raw policy string. Checks "
                    "unsafe-inline, unsafe-eval, a bare *, default-src and "
                    "frame-ancestors. Exits 1 on any finding.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--headers", metavar="FILE",
                       help="JSON dump of response headers")
    group.add_argument("--policy", metavar="CSP",
                       help="raw Content-Security-Policy value")
    parser.add_argument("--verbose", action="store_true",
                        help="print one line of detail per finding")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        if args.headers:
            headers = load_headers(args.headers)
            policies = headers.get(HEADER) or [""]
        else:
            policies = [args.policy]
    except ValueError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    findings = []
    seen = set()
    for policy in policies:
        for label, detail in audit(policy):
            if label in seen:
                continue
            seen.add(label)
            findings.append((label, detail))

    if findings:
        print("FAIL %d csp finding(s)" % len(findings))
        print("; ".join(label for label, _ in findings))
        if args.verbose:
            for label, detail in findings:
                print("  %s: %s" % (label, detail))
        return 1

    print("OK csp clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
