---
id: p566
title: "An API key age report in Python"
slug: an-api-key-age-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, APIKeys, Security, DevSecOps, Automation]
source: "LinkedIn post P566 · PythonSec series"
linkedin_date: 2030-05-09
design: code
script: key_age.py
---

# An API key age report in Python

Eight API keys sit in an inventory, and the oldest was created 412 days ago and has never been used. Nobody notices until the next audit, because the inventory is a file and nobody reads a file.

## Quick reference

The full script is at the end of this note: `key_age.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 key_age.py keys.json --max-days 180 --now 2026-10-21
```

**Example output**

```text
FLAG svc-legacy 412d never
BUCKETS 3 2 1 2
```

## Explained

### What it does

The script reads the inventory JSON, parses created_at and last_used, and computes the age of every key against a reference time. It flags a key when the age is above `--max-days` or when last_used is null, then prints four age buckets, thirty days each with the last one open-ended, so the shape of the estate is visible.

### The output

The run above prints one FLAG line for the old key, with its age in days and never, then BUCKETS 3 2 1 2. Each bucket covers thirty days; the last one holds everything from 90 days up. A used key over the threshold prints its last-used date instead of never.

### The exit code

0 means no key is stale and none is unused, 1 means at least one flag, 2 means the file, the JSON or a record was bad. That makes the report a gate: a weekly job can fail the review instead of filling an inbox.

> **The honest caveat:** last_used is only as good as the inventory. A key used by a quarterly batch job looks unused today, and a key marked used can still be live after its owner left.

> **The lesson:** age is a proxy for risk, so use it to ask, not to assume.

## In one line

> **Old and unused is a finding.** Age is a question; the owner has to answer it.

**Set the policy**

```bash
--max-days 90
```

## Script: key_age.py

Download: [scripts/key_age.py](../scripts/key_age.py)

```python
#!/usr/bin/env python3
"""key_age.py - report stale and unused API keys from an inventory JSON.

Reads an inventory of key metadata (never key material) and prints the keys
that are older than a threshold or have never been used. Four age buckets
(0-29, 30-59, 60-89 and 90+ days) summarise the inventory, so the report says
what to fix and how the estate is ageing.

Inventory shape, a JSON object with a "keys" list (a bare list also works):

    {"keys": [
      {"id": "svc-billing", "owner": "platform",
       "created_at": "2026-01-04T09:00:00Z",
       "last_used": "2026-10-01T12:00:00Z"},
      {"id": "svc-ci", "owner": "build",
       "created_at": "2024-08-30T09:00:00Z", "last_used": null}
    ]}

Usage:
    python3 key_age.py keys.json
    python3 key_age.py keys.json --max-days 180
    python3 key_age.py keys.json --now 2026-10-21T00:00:00Z
    cat keys.json | python3 key_age.py -
    python3 key_age.py --help

CI (fail the job when a key is older than the policy):
    python3 key_age.py keys.json --max-days 90 || exit 1

Cron (weekly report to the security channel):
    0 7 * * 1 python3 /opt/s0sta/key_age.py /etc/s0sta/keys.json --max-days 90

Exit codes: 0 no key is stale and none is unused, 1 at least one flag,
2 usage, unreadable input or a record that does not match the schema.

Read-only: the inventory is opened for reading only. No key is created,
rotated or revoked, and no network call is made.

The inventory holds identifiers and timestamps, not secrets. This script
never asks for, prints or stores a key value.

By s0sta.com
"""
import argparse
import json
import sys
from datetime import datetime, timezone

BUCKET_DAYS = 30
BUCKETS = 4


def parse_time(text, field, where):
    """Parse an ISO 8601 timestamp; a naive value is treated as UTC."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("%s: %s is not a timestamp" % (where, field))
    raw = text.strip()
    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"
    try:
        value = datetime.fromisoformat(raw)
    except ValueError:
        raise ValueError("%s: %s is not ISO 8601: %r" % (where, field, text))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def load_inventory(path):
    """Return the list of key records, or raise ValueError."""
    try:
        if path == "-":
            document = json.load(sys.stdin)
        else:
            with open(path, "r", encoding="utf-8") as handle:
                document = json.load(handle)
    except OSError as exc:
        raise ValueError("%s: %s" % (path, exc))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("%s: not valid JSON: %s" % (path, exc))
    if isinstance(document, dict):
        keys = document.get("keys")
    else:
        keys = document
    if not isinstance(keys, list):
        raise ValueError("%s: expected a list or an object with a keys list"
                         % path)
    return keys


def check_record(record, index):
    """Validate one record; return a label for error messages."""
    where = "key %d" % (index + 1)
    if not isinstance(record, dict):
        raise ValueError("%s is not an object" % where)
    for field in ("id", "owner", "created_at"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError("%s: %s is missing" % (where, field))
    last_used = record.get("last_used")
    if last_used is not None and not isinstance(last_used, str):
        raise ValueError("%s: last_used must be a string or null" % where)
    return where


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Report API keys that are too old or never used.")
    parser.add_argument("inventory", nargs="?", default="-",
                        help="inventory JSON file; stdin when omitted")
    parser.add_argument("--max-days", type=int, default=90,
                        help="flag keys older than this (default 90)")
    parser.add_argument("--now",
                        help="ISO 8601 reference time for the report")
    args = parser.parse_args(argv)
    if args.max_days < 1:
        parser.error("--max-days must be a positive integer")
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        records = load_inventory(args.inventory)
        if args.now:
            as_of = parse_time(args.now, "--now", "arguments")
        else:
            as_of = datetime.now(timezone.utc)
        buckets = [0] * BUCKETS
        flags = 0
        for index, record in enumerate(records):
            where = check_record(record, index)
            created = parse_time(record["created_at"], "created_at", where)
            age = (as_of - created).days
            if age < 0:
                raise ValueError("%s: created_at is in the future" % where)
            last_used = record.get("last_used")
            if last_used:
                parse_time(last_used, "last_used", where)
            buckets[min(age // BUCKET_DAYS, BUCKETS - 1)] += 1
            if age > args.max_days or not last_used:
                flags += 1
                used = "never" if not last_used else "last=%s" % last_used[:10]
                print("FLAG %s %dd %s" % (record["id"], age, used))
        print("BUCKETS " + " ".join(str(count) for count in buckets))
    except ValueError as exc:
        print("key_age: %s" % exc, file=sys.stderr)
        return 2
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main())
```
