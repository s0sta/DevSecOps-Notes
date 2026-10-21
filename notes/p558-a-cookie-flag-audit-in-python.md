---
id: p558
title: "A cookie flag audit in Python"
slug: a-cookie-flag-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Cookies, WebSecurity, Python, DevSecOps, HTTP]
source: "LinkedIn post P558 · PythonSec series"
linkedin_date: 2030-04-21
design: code
script: cookie_audit.py
---

# A cookie flag audit in Python

A session cookie with no flags is a password in a paper bag. The browser will send it over plain HTTP, script can read it, and another site can borrow it. A framework default is not an audit, and these flags are often unset.

## Quick reference

The full script is at the end of this note: `cookie_audit.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 cookie_audit.py --headers /tmp/h.json
```

**Example output**

```text
FAIL session: 4 issue(s)
Secure; HttpOnly; SameSite; Max-Age 31536000 too long
```

## Explained

### What it checks

The script parses Set-Cookie headers from a headers dump or one raw value. It never prints the cookie value, only the name. For each cookie it checks Secure, HttpOnly, SameSite, and a Max-Age above the ceiling, which defaults to thirty days. Expires is ignored, because Max-Age is the modern attribute. A cookie without Max-Age is a session cookie, so its lifetime is not flagged.

### The run

The dirty sample prints two lines: FAIL session: 4 issue(s), then Secure; HttpOnly; SameSite; Max-Age 31536000 too long. Exit 1 fails the job, a clean cookie exits 0, and a malformed header exits 2. The full script is attached, standard library only and read-only.

### Why each

Secure keeps the cookie off plain HTTP. HttpOnly keeps it away from document.cookie. SameSite stops another origin from sending it on a cross-site request. The Max-Age check catches a token that outlives its welcome by a year.

> **The honest caveat:** Chrome and Firefox now default to Lax, so a missing attribute is less dangerous than it was; the missing Secure and HttpOnly flags are the ones to fix first. A short Max-Age also does not shorten a server-side session.

> **The lesson:** flags are cheap, and their absence is visible.

## In one line

> **A cookie is a policy, not a value.** The flags decide where the token may travel and who may read it.

**Check the flags**

```bash
python3 cookie_audit.py --headers h.json
```

## Script: cookie_audit.py

Download: [scripts/cookie_audit.py](../scripts/cookie_audit.py)

```python
#!/usr/bin/env python3
"""Audit Set-Cookie headers for missing flags and a long lifetime.

Reads a response-headers JSON dump, or one raw Set-Cookie value, and flags:

    Secure       the cookie may travel over plain HTTP
    HttpOnly     document.cookie can read the value
    SameSite     cross-site requests may send the cookie
    Max-Age      the lifetime is longer than the ceiling, default 30 days

The cookie value is never printed. Only the name, the flags and the Max-Age
number appear in the output, so a session token in the fixture stays out of
the logs.

Usage:
    python3 cookie_audit.py --headers /tmp/headers.json
    python3 cookie_audit.py --cookie "session=abc; Path=/; HttpOnly"
    python3 cookie_audit.py --headers /tmp/headers.json --max-age 86400
    python3 cookie_audit.py --headers /tmp/headers.json --verbose
    python3 cookie_audit.py --help

A headers dump may be an object of names to values, an object with a
"headers" object, or a list of {"name": ..., "value": ...} entries. The
set-cookie entry may be one string or a list of strings.

CI (after a deploy):
    python3 cookie_audit.py --headers /tmp/headers.json || exit 1

Cron (daily at 06:15):
    15 6 * * * python3 /opt/s0sta/cookie_audit.py --headers /var/tmp/h.json

Exit codes: 0 clean, 1 at least one finding, 2 usage or unreadable input.
Read-only: the file is read, nothing is written, nothing is fetched.

Expires is not parsed: Max-Age is the modern attribute and the one that
survives a browser restart consistently. A short Max-Age is not proof of a
short session, because the server can still expire the token.

By s0sta.com
"""
import argparse
import json
import sys

HEADER = "set-cookie"


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
            if isinstance(entry, str):
                items.append((HEADER, entry))
                continue
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


def parse_cookie(raw):
    """Return (name, attributes) for one Set-Cookie value."""
    parts = raw.split(";")
    pair = parts[0].strip()
    if "=" not in pair:
        raise ValueError("set-cookie value has no name=value pair")
    name = pair.split("=", 1)[0].strip()
    if not name:
        raise ValueError("set-cookie value has an empty name")
    attrs = {}
    for part in parts[1:]:
        text = part.strip()
        if not text:
            continue
        key, _, value = text.partition("=")
        attrs[key.strip().lower()] = value.strip()
    return name, attrs


def audit(attrs, max_age):
    """Return a list of (label, detail) findings for one cookie."""
    findings = []
    if "secure" not in attrs:
        findings.append(("Secure", "the cookie can travel over plain HTTP"))
    if "httponly" not in attrs:
        findings.append(("HttpOnly", "document.cookie can read the value"))
    if "samesite" not in attrs:
        findings.append(("SameSite", "cross-site requests may send the cookie"))
    raw_age = attrs.get("max-age", "")
    if raw_age:
        try:
            seconds = int(raw_age)
        except ValueError:
            findings.append(("Max-Age invalid",
                             "Max-Age %r is not an integer" % raw_age))
        else:
            if seconds > max_age:
                findings.append(("Max-Age %d too long" % seconds,
                                 "%d seconds is above the %d second ceiling"
                                 % (seconds, max_age)))
    return findings


def positive_int(text):
    """argparse type: a whole number greater than zero."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("%r is not a whole number" % text)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return value


def build_parser():
    """Return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="cookie_audit.py",
        description="Flag Set-Cookie headers without Secure, HttpOnly or "
                    "SameSite, and cookies whose Max-Age is above the "
                    "ceiling. The value is never printed. Exits 1 on any "
                    "finding.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--headers", metavar="FILE",
                       help="JSON dump of response headers")
    group.add_argument("--cookie", metavar="VALUE",
                       help="one raw Set-Cookie value")
    parser.add_argument("--max-age", type=positive_int, default=2592000,
                        metavar="SECONDS",
                        help="longest acceptable Max-Age (default: 2592000, "
                             "30 days)")
    parser.add_argument("--verbose", action="store_true",
                        help="print one line of detail per finding")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        if args.headers:
            headers = load_headers(args.headers)
            cookies = headers.get(HEADER, [])
            if not cookies:
                print("OK 0 cookie(s), nothing to audit")
                return 0
        else:
            cookies = [args.cookie]
        parsed = [parse_cookie(raw) for raw in cookies]
    except ValueError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    failed = 0
    for name, attrs in parsed:
        findings = audit(attrs, args.max_age)
        if not findings:
            continue
        failed += 1
        print("FAIL %s: %d issue(s)" % (name, len(findings)))
        print("; ".join(label for label, _ in findings))
        if args.verbose:
            for label, detail in findings:
                print("  %s: %s" % (label, detail))

    if failed:
        return 1
    print("OK %d cookie(s) with all flags set" % len(parsed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
