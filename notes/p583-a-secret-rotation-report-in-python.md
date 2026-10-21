---
id: p583
title: "A secret rotation report in Python"
slug: a-secret-rotation-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, SecretsManagement, DevSecOps, CyberSecurity, Automation]
source: "LinkedIn post P583 · PythonFixes series"
linkedin_date: 2030-06-18
design: code
script: secret_rotation_due.py
---

# A secret rotation report in Python

A production token issued in 2023 was still valid this month. Rotation was a calendar reminder, the reminder moved with a meeting, and nobody could say when the secret had last changed.

## Quick reference

The full script is at the end of this note: `secret_rotation_due.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 secret_rotation_due.py /tmp/secrets.json
```

**Example output**

```text
DUE db-password prod 290
NEVER api-token prod
```

## Explained

### What it does

It reads a secret inventory and computes the age of every entry from last_rotated. A secret past its own max_age_days is DUE; a null date is NEVER. The per-record window wins, and `--max-days` supplies the default. On screen the loop prints DUE db-password prod 290 and NEVER api-token prod, then exits 1.

### How to run it

`python3 secret_rotation_due.py secrets.json --max-days 90`. The Monday cron line is in the docstring. In CI, run it against the inventory in the same repository as the service, so a new secret cannot merge without a rotation date.

### The fix

Rotate the DUE entries first, oldest first, and write the new date as part of the same change. Add the NEVER entries to the inventory before you rotate them, or the next report will still be blind. The inventory holds names and dates, never values.

### Prevention

Keep the inventory in Git and review it like code. A pull request that adds a secret adds its rotation window in the same diff. The check then fails the pipeline when the window closes, instead of asking a person to remember.

> **The honest caveat:** an inventory is a claim. A secret rotated outside the process is invisible, and a recent date does not prove the value changed.

> **The lesson:** a rotation you cannot prove is a guess.

## In one line

> **A rotation you cannot prove is a guess.** A date in an inventory is the only evidence that rotation happened.

**Run it monday**

```bash
python3 secret_rotation_due.py secrets.json
```

## Script: secret_rotation_due.py

Download: [scripts/secret_rotation_due.py](../scripts/secret_rotation_due.py)

```python
#!/usr/bin/env python3
"""secret_rotation_due.py - report secrets past their rotation window.

Reads a secret inventory (metadata only, never a secret value) and prints the
entries that are older than their own max_age_days or were never rotated. The
inventory is the missing control in most estates: everyone believes rotation
happens, nobody can show when it last did.

Inventory shape, a JSON object with a "secrets" list (a bare list also works):

    {"secrets": [
      {"name": "db-password", "env": "prod",
       "last_rotated": "2026-01-04", "max_age_days": 90},
      {"name": "api-token", "env": "prod",
       "last_rotated": null, "max_age_days": 30}
    ]}

last_rotated is an ISO 8601 date or timestamp, or null for never rotated.
max_age_days is optional; --max-days supplies the default.

Usage:
    python3 secret_rotation_due.py secrets.json
    python3 secret_rotation_due.py secrets.json --max-days 60
    python3 secret_rotation_due.py secrets.json --now 2026-10-21
    cat secrets.json | python3 secret_rotation_due.py -
    python3 secret_rotation_due.py --help

CI (fail the job when a secret is past its window):
    python3 secret_rotation_due.py secrets.json --max-days 90 || exit 1

Cron (Monday morning report to the security channel):
    0 7 * * 1 python3 /opt/s0sta/secret_rotation_due.py /etc/s0sta/secrets.json

Exit codes: 0 every secret is inside its window, 1 at least one is due or
never rotated, 2 usage error or unreadable, invalid or empty input.

Read-only: the inventory is opened for reading only. Nothing is rotated,
created or revoked and no network call is made. The inventory holds names,
environments and dates; this script never asks for and never prints a secret
value. A rotation performed outside the inventory is invisible to it.

By s0sta.com
"""
import argparse
import json
import sys
from datetime import datetime, timezone


class InputError(Exception):
    """An input that cannot be audited."""


def parse_time(text, field, where):
    """Parse an ISO 8601 date or timestamp as an aware UTC datetime."""
    if not isinstance(text, str) or not text.strip():
        raise InputError("%s: %s is not a timestamp" % (where, field))
    raw = text.strip()
    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"
    try:
        value = datetime.fromisoformat(raw)
    except ValueError:
        raise InputError("%s: %s is not ISO 8601: %r" % (where, field, text))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def load_inventory(path):
    """Return the list of secret records, or raise InputError."""
    try:
        if path == "-":
            document = json.load(sys.stdin)
        else:
            with open(path, "r", encoding="utf-8") as handle:
                document = json.load(handle)
    except OSError as exc:
        raise InputError("%s: %s" % (path, exc.strerror or exc))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise InputError("%s: not valid JSON: %s" % (path, exc))
    if isinstance(document, dict):
        records = document.get("secrets")
    else:
        records = document
    if not isinstance(records, list):
        raise InputError("%s: expected a list or an object with a secrets list"
                         % path)
    return records


def check_record(record, index, default_days):
    """Validate one record; return (where, name, env, last, max_days)."""
    where = "secret %d" % (index + 1)
    if not isinstance(record, dict):
        raise InputError("%s is not an object" % where)
    for field in ("name", "env"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise InputError("%s: %s is missing" % (where, field))
    last = record.get("last_rotated")
    if last is not None and not isinstance(last, str):
        raise InputError("%s: last_rotated must be a string or null" % where)
    max_days = record.get("max_age_days", default_days)
    if not isinstance(max_days, int) or isinstance(max_days, bool):
        raise InputError("%s: max_age_days must be an integer" % where)
    if max_days < 1:
        raise InputError("%s: max_age_days must be positive" % where)
    return where, record["name"].strip(), record["env"].strip(), last, max_days


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Report secrets past their rotation window (read-only).")
    parser.add_argument("inventory", nargs="?", default="-",
                        help="inventory JSON file; stdin when omitted")
    parser.add_argument("--max-days", type=int, default=90,
                        help="default rotation window in days (default 90)")
    parser.add_argument("--now", help="ISO 8601 reference time for the report")
    args = parser.parse_args(argv)
    if args.max_days < 1:
        parser.error("--max-days must be a positive integer")
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        if args.now:
            now = parse_time(args.now, "--now", "arguments")
        else:
            now = datetime.now(timezone.utc)
        records = load_inventory(args.inventory)
        flags = 0
        for index, record in enumerate(records):
            where, name, env, last, max_days = check_record(
                record, index, args.max_days)
            if last is None:
                flags += 1
                print("NEVER %s %s (no rotation record)" % (name, env))
                continue
            rotated = parse_time(last, "last_rotated", where)
            age = (now - rotated).days
            if age < 0:
                raise InputError("%s: last_rotated is in the future" % where)
            if age > max_days:
                flags += 1
                print("DUE %s %s %dd (max %dd)" % (name, env, age, max_days))
    except InputError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2
    total = len(records) if isinstance(records, list) else 0
    if flags:
        noun = "secret" if total == 1 else "secrets"
        print("FINDING %d of %d %s past their window" % (flags, total, noun))
        return 1
    if total == 1:
        print("OK 1 secret inside its window")
    else:
        print("OK %d secrets inside their windows" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
