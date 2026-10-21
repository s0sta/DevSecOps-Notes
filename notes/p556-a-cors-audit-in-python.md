---
id: p556
title: "A CORS audit in Python"
slug: a-cors-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [CORS, API, WebSecurity, Python, DevSecOps]
source: "LinkedIn post P556 · PythonSec series"
linkedin_date: 2030-04-16
design: code
script: cors_audit.py
---

# A CORS audit in Python

A CORS bug rarely looks like one. The header is present, the request works, and the response is readable from a domain that should never see it.

## Quick reference

The full script is at the end of this note: `cors_audit.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 cors_audit.py /tmp/cors.json
```

**Example output**

```text
FAIL 2 cors finding(s)
reflected origin + credentials; null origin
```

## Explained

### What it reads

The script takes a JSON file with one response sample or a list of them. A sample has a request_origin and either a headers object or the headers at the top level. The script also accepts a configuration object with allow_origins and allow_credentials. Header names are matched case-insensitively, so a dump from nginx and a dump from curl both work.

### What it flags

Three patterns fail the run. A wildcard origin together with credentials set to true, which browsers reject but a proxy can rewrite into something worse. An origin the response echoes back, unless it appears in allowed_origins. A null origin, which any sandboxed frame can claim. A wildcard without credentials is not flagged, because public CORS is a valid design.

### The run

On the sample file it prints two lines: FAIL 2 cors finding(s), then reflected origin + credentials; null origin. Exit 1 fails the job, a clean allowlist exits 0, and a broken file exits 2. The full script is attached, standard library only and read-only.

> **The honest caveat:** one sample proves one response. Send two different Origins and compare, because a server that echoes both is reflecting whatever the config says. CORS is also not authentication: it only decides who may read.

> **The lesson:** an echoed Origin is a wildcard with extra steps.

## In one line

> **Echo is not an allowlist.** An origin sent back unchanged is a wildcard with extra steps.

**Test two origins**

```bash
python3 cors_audit.py cors.json
```

## Script: cors_audit.py

Download: [scripts/cors_audit.py](../scripts/cors_audit.py)

```python
#!/usr/bin/env python3
"""Audit CORS headers or a CORS configuration for three common mistakes.

Reads a JSON file holding one response sample, a list of samples, or a
configuration object, and flags:

    wildcard * + credentials   any origin may send authenticated requests
    reflected origin           the response echoes the caller's Origin
    null origin                sandboxed frames and data: URLs get access

A response sample has a "headers" object and an optional "request_origin".
A flat object whose keys are header names also works, which is what a curl
dump looks like. A configuration object uses "allow_origins" (a string or a
list) and "allow_credentials" (true or false).

A wildcard without credentials is not flagged: public, unauthenticated CORS
is a valid design. A reflected origin is only flagged when it is not listed
in the sample's optional "allowed_origins" list, so a deliberate allowlist
that echoes one approved origin is not a finding.

Usage:
    python3 cors_audit.py /tmp/cors.json
    python3 cors_audit.py /tmp/cors-config.json
    python3 cors_audit.py /tmp/cors.json --verbose
    python3 cors_audit.py --help

CI (after a deploy):
    python3 cors_audit.py /tmp/cors.json || exit 1

Cron (daily at 06:30):
    30 6 * * * python3 /opt/s0sta/cors_audit.py /var/tmp/cors.json

Exit codes: 0 clean, 1 at least one finding, 2 usage or unreadable input.
Read-only: the file is read, nothing is written, nothing is fetched.

The honest limit: one response sample proves what the server does for one
Origin. To prove reflection, send two different Origins and compare; this
script can only judge the samples it is given.

By s0sta.com
"""
import argparse
import json
import sys

ALLOW_ORIGIN = "access-control-allow-origin"
ALLOW_CREDENTIALS = "access-control-allow-credentials"


def load_json(path):
    """Read one JSON document and return it."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    except json.JSONDecodeError as exc:
        raise ValueError("%s is not valid JSON: %s" % (path, exc))


def normalize_headers(raw):
    """Return a lowercase {header: [values]} map."""
    headers = {}
    for name, value in raw.items():
        values = value if isinstance(value, list) else [value]
        clean = [str(item).strip() for item in values if item is not None]
        if clean:
            headers[str(name).lower()] = clean
    return headers


def first(headers, name):
    """Return the first value of a header, lowercased, or an empty string."""
    values = headers.get(name)
    return values[0].lower() if values else ""


def truthy(value):
    """Read a JSON boolean that may also be the string true."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def origin_list(value):
    """Return a lowercase list of origins from a string or a list."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ValueError("allow_origins must be a string or a list")
    return [str(item).strip().lower() for item in value]


def is_config(sample):
    """True when the object is a CORS configuration, not a response dump."""
    if "allow_origins" not in sample or "headers" in sample:
        return False
    keys = [str(key).lower() for key in sample]
    return ALLOW_ORIGIN not in keys and ALLOW_CREDENTIALS not in keys


def audit_config(sample):
    """Return a list of (label, detail) findings for a configuration."""
    origins = origin_list(sample.get("allow_origins"))
    credentials = truthy(sample.get("allow_credentials", False))
    findings = []
    if "*" in origins and credentials:
        findings.append(("wildcard * + credentials",
                         "allow_origins is * while credentials are allowed"))
    if "null" in origins:
        findings.append(("null origin",
                         "the null origin is allowed in the configuration"))
    return findings


def audit_response(sample):
    """Return a list of (label, detail) findings for one response sample."""
    if isinstance(sample.get("headers"), dict):
        raw = sample["headers"]
    else:
        raw = {key: value for key, value in sample.items()
               if str(key).lower() not in ("request_origin", "allowed_origins")}
    headers = normalize_headers(raw)
    origin = str(sample.get("request_origin", "")).strip().lower()
    allowed = origin_list(sample.get("allowed_origins"))
    acao = first(headers, ALLOW_ORIGIN)
    credentials = first(headers, ALLOW_CREDENTIALS) == "true"
    findings = []

    if acao == "*" and credentials:
        findings.append(("wildcard * + credentials",
                         "the response allows any origin with credentials"))
    if (acao and origin and acao == origin and origin != "null"
            and acao != "null" and origin not in allowed):
        label = "reflected origin"
        if credentials:
            label += " + credentials"
        findings.append((label, "the response echoes the request Origin"))
    if acao == "null":
        findings.append(("null origin",
                         "the response allows the null origin"))
    return findings


def build_parser():
    """Return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="cors_audit.py",
        description="Flag wildcard-with-credentials, reflected origins and "
                    "null origins in a CORS headers dump or configuration. "
                    "Exits 1 on any finding.")
    parser.add_argument("file", metavar="JSON",
                        help="response sample, list of samples, or config")
    parser.add_argument("--verbose", action="store_true",
                        help="print one line of detail per finding")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        data = load_json(args.file)
        samples = data if isinstance(data, list) else [data]
        if not samples:
            raise ValueError("the JSON file holds no samples")
        for sample in samples:
            if not isinstance(sample, dict) or not sample:
                raise ValueError("each sample must be a non-empty object")
            if "headers" in sample and not isinstance(sample["headers"], dict):
                raise ValueError("the headers field must be an object")
    except ValueError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    findings = []
    seen = set()
    try:
        for sample in samples:
            found = (audit_config(sample) if is_config(sample)
                     else audit_response(sample))
            for label, detail in found:
                if label in seen:
                    continue
                seen.add(label)
                findings.append((label, detail))
    except ValueError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    if findings:
        print("FAIL %d cors finding(s)" % len(findings))
        print("; ".join(label for label, _ in findings))
        if args.verbose:
            for label, detail in findings:
                print("  %s: %s" % (label, detail))
        return 1

    print("OK cors clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
