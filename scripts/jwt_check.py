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
