---
id: p360
title: "A data freshness checker in Python"
slug: a-data-freshness-checker-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [DataEngineering, Python, DataQuality, DataOps, Analytics]
source: "LinkedIn post P360 · Data series"
linkedin_date: 2029-01-14
design: code
script: freshness_check.py
---

# A data freshness checker in Python

The orders table stopped updating at 2am and the dashboard looks normal, because yesterday's numbers are still there. Freshness is the check nobody writes until the first silent failure.

## Quick reference

The full script is at the end of this note: **freshness_check.py** (standard library only, no `pip install`).

**Run it**

```bash
python3 freshness_check.py fresh.json --max-age 60
```

**Example output**

```text
STALE 720 warehouse.customers
1 of 2 stale
```

## Explained

**What it reads**  
The script takes a JSON map of table name to last-updated timestamp, from a file or stdin. The timestamps are ISO 8601, and a trailing Z or an explicit offset both work.

**How it decides**  
For each table it subtracts the timestamp from now, in minutes. A table older than `--max-age` prints as STALE and joins the list; the rest print ok. Both sides of the subtraction are UTC, so a server in another zone does not move the line.

**Exit codes**  
Exit 0 means every table is inside the window, exit 1 means at least one is stale, and exit 2 means the file was unreadable, the JSON was malformed or a timestamp would not parse. Exit 2 is a broken check, not a clean result. The attached script is standard library only, read-only, and takes `--max-age` and `--now`.

> **The honest caveat:** a timestamp written by the job that loads the table proves the job ran, not that it wrote new rows. Point the check at a heartbeat the pipeline updates itself, or at the maximum updated_at in the table.

> **The lesson:** a table that stopped moving looks exactly like a quiet day, unless something counts the minutes.

## In one line

> **A table that stopped moving.** A silent failure looks exactly like a quiet day.

**Run it in ci**

```bash
python3 freshness_check.py fresh.json
```

## Script: freshness_check.py

Download: [scripts/freshness_check.py](../scripts/freshness_check.py)

```python
#!/usr/bin/env python3
"""Fail when a table in a JSON freshness map has not been updated in time.

The map is one JSON object of table name to ISO 8601 timestamp:

    {"warehouse.orders": "2026-10-20T20:30:00Z",
     "warehouse.customers": "2026-10-19T09:00:00Z"}

Usage:
    python3 freshness_check.py fresh.json --max-age 60

    cat fresh.json | python3 freshness_check.py - --max-age 60

    python3 freshness_check.py fresh.json --now 2026-10-20T21:00:00Z

Exit codes:
    0  every table is inside the window
    1  at least one table is stale
    2  unreadable input, bad JSON or an unparsable timestamp

Cron/CI:
    15 * * * * python3 /srv/checks/freshness_check.py \
        /srv/checks/fresh.json --max-age 60

By s0sta.com
"""
import argparse
import json
import sys
from datetime import datetime, timezone


def parse_stamp(text):
    """Parse an ISO 8601 timestamp and return it in UTC."""
    value = text.strip().replace("Z", "+00:00")
    stamp = datetime.fromisoformat(value)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="freshness_check.py",
        description="Flag tables whose last_updated timestamp is older than "
                    "--max-age, from a JSON map of table to timestamp.")
    parser.add_argument("source", nargs="?", default="-",
                        help="JSON map file, or - for stdin (default: -)")
    parser.add_argument("--max-age", type=int, default=60, metavar="MINUTES",
                        help="minutes before a table counts as stale (default: 60)")
    parser.add_argument("--now", metavar="ISO8601",
                        help="evaluate against this time instead of the clock")
    args = parser.parse_args(argv)

    if args.max_age < 0:
        parser.error("--max-age must be zero or more")

    try:
        if args.source == "-":
            raw = sys.stdin.read()
        else:
            with open(args.source) as handle:
                raw = handle.read()
    except OSError as exc:
        print("error: cannot read %s: %s" % (args.source, exc), file=sys.stderr)
        return 2

    try:
        tables = json.loads(raw)
    except ValueError as exc:
        print("error: not valid JSON: %s" % exc, file=sys.stderr)
        return 2
    if not isinstance(tables, dict) or not tables:
        print("error: expected a non-empty JSON object of table to timestamp",
              file=sys.stderr)
        return 2

    try:
        now = parse_stamp(args.now) if args.now else datetime.now(timezone.utc)
    except ValueError as exc:
        print("error: bad --now value: %s" % exc, file=sys.stderr)
        return 2

    stale = []
    for name in sorted(tables):
        try:
            stamp = parse_stamp(str(tables[name]))
        except ValueError:
            print("error: %s has an unparsable timestamp: %r"
                  % (name, tables[name]), file=sys.stderr)
            return 2
        minutes = int((now - stamp).total_seconds() // 60)
        if minutes < 0:
            print("%-6s %5dm %s" % ("FUTURE", -minutes, name))
            stale.append(name)
            continue
        flag = "STALE" if minutes > args.max_age else "ok"
        print("%-6s %5dm %s" % (flag, minutes, name))
        if minutes > args.max_age:
            stale.append(name)

    print("%d of %d tables stale after %d minutes"
          % (len(stale), len(tables), args.max_age))
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
```
