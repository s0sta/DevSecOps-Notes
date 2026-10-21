---
id: p406
title: "A JWT checker in Python"
slug: a-jwt-checker-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [JWT, AppSec, Python, CyberSecurity, DevSecOps]
source: "LinkedIn post P406 · DevSecOps series"
linkedin_date: 2029-05-01
design: code
script: jwt_check.py
---

# A JWT checker in Python

A JWT is not a session; it is a signed claim. Before you trust one, read what it says. This script decodes the header and payload, checks the claims that cause trouble, and never verifies the signature.

## Quick reference

The full script is at the end of this note: `jwt_check.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 jwt_check.py "$TOKEN"
```

**Example output**

```text
ALERT no exp no aud
```

## Explained

### What the GIF shows

The 14-line core pads and decodes the first two parts of the token. It lowercases alg, so alg none is caught whatever the case. It reads exp once, then reports a missing or expired exp, or a lifetime over 86,400 seconds. Finally it collects a missing iss and aud, prints ALERT and exits 1.

### The checks

alg none is the old bypass: a verifier that trusts the header can be told there is no signature. exp is a NumericDate in seconds since the epoch, and a token without it never expires. iss and aud tie a token to an issuer and an audience; without them, a token for one service may be accepted by another. A token valid for a week is a stolen token valid for a week.

### Running it

`python3 jwt_check.py "$TOKEN"`, from cron or a CI step over your token fixtures. The attached script adds argparse, `--max-hours`, file input and clear exit codes: 0 clean, 1 findings, 2 bad input. It is read-only.

> **The honest caveat:** this is a claim linter, not an authenticator. It does not verify the signature, so a clean result says the claims look sane, not that the token is genuine; most libraries reject alg none by default.

> **The lesson:** decode first, verify separately, and never accept a token because it parsed.

## In one line

> **A claim is not a promise.** Decode first; verify the signature somewhere else.

**Run it in ci**

```bash
python3 jwt_check.py "$TOKEN"
```

## Script: jwt_check.py

Download: [scripts/jwt_check.py](../scripts/jwt_check.py)

```python
#!/usr/bin/env python3
"""jwt_check.py - inspect JWT claims without verifying the signature.

Decodes the header and payload of a JSON Web Token and reports the claim
problems reviewers look for: alg none, a missing or expired exp, a lifetime
over the limit, and a missing iss or aud. It never checks the signature, so
it must not be used to accept a token. Read-only: it decodes and makes no
network calls. Standard library only, Python 3.8+.

Usage:
    python3 jwt_check.py <token>
    python3 jwt_check.py --file token.txt
    python3 jwt_check.py --stdin < token.txt
    python3 jwt_check.py --max-hours 12 <token>

Run it from cron on a token you already hold, or as a CI step over the test
fixtures that contain sample tokens.

Exit codes: 0 clean, 1 findings, 2 usage or input error.

By s0sta.com
"""
import argparse
import base64
import binascii
import json
import re
import sys
import time

DEFAULT_MAX_HOURS = 24
PART_RE = re.compile(r"^[A-Za-z0-9_-]*$")


def decode_segment(part, name):
    """Decode one base64url segment into a JSON object."""
    if not part:
        raise ValueError("empty %s segment" % name)
    if not PART_RE.match(part):
        raise ValueError("%s segment is not base64url" % name)
    padded = part + "=" * (-len(part) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        obj = json.loads(raw.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, ValueError) as exc:
        raise ValueError("cannot decode %s segment: %s" % (name, exc))
    if not isinstance(obj, dict):
        raise ValueError("%s segment is not a JSON object" % name)
    return obj


def parse_token(token):
    """Split a JWT and return its header and payload as dicts."""
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValueError("a JWT has three dot-separated parts, got %d" % len(parts))
    return decode_segment(parts[0], "header"), decode_segment(parts[1], "payload")


def find_claims(header, payload, max_hours, now=None):
    """Return a list of findings; an empty list means the claims look sane."""
    now = time.time() if now is None else now
    bad = []
    alg = str(header.get("alg", "")).lower()
    if alg == "none":
        bad.append("alg=none")
    exp = payload.get("exp")
    if exp is None:
        bad.append("no exp")
    elif isinstance(exp, bool) or not isinstance(exp, (int, float)):
        bad.append("exp is not a number")
    elif exp < now:
        bad.append("expired")
    elif exp - now > max_hours * 3600:
        bad.append("long-lived")
    if not payload.get("iss"):
        bad.append("no iss")
    if not payload.get("aud"):
        bad.append("no aud")
    return bad


def read_token(args):
    """Return the token text from the positional, --file or --stdin."""
    if args.token:
        return args.token
    if args.file:
        with open(args.file) as fh:
            return fh.read().strip()
    if args.stdin:
        return sys.stdin.read().strip()
    raise ValueError("give a token, or use --file or --stdin")


def main():
    ap = argparse.ArgumentParser(
        description="Decode a JWT and flag claim problems without verifying it.",
        epilog="Exit codes: 0 clean, 1 findings, 2 usage or input error.",
    )
    ap.add_argument("token", nargs="?", help="the JWT, as one argument")
    ap.add_argument("-f", "--file", help="read the token from a file")
    ap.add_argument("--stdin", action="store_true", help="read the token from stdin")
    ap.add_argument("--max-hours", type=float, default=DEFAULT_MAX_HOURS,
                    help="flag lifetimes longer than this (default: %(default)s)")
    args = ap.parse_args()

    try:
        token = read_token(args)
        if not token:
            raise ValueError("the token is empty")
        if args.max_hours <= 0:
            raise ValueError("--max-hours must be greater than zero")
        header, payload = parse_token(token)
    except (OSError, ValueError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    bad = find_claims(header, payload, args.max_hours)
    if bad:
        print("ALERT " + " ".join(bad))
        return 1
    print("OK alg=%s, claims look sane (signature not checked)"
          % header.get("alg", "missing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
