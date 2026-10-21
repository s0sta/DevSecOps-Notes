---
id: p465
title: "A review latency report in Python"
slug: a-review-latency-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, DeveloperExperience, CodeReview, CICD, DevOps]
source: "LinkedIn post P465 · DevOps series"
linkedin_date: 2029-09-16
design: code
script: review_latency.py
---

# A review latency report in Python

A pull request opened on Monday and reviewed on Wednesday costs more than the review itself. The delay is measurable from the API export you already have.

## Quick reference

The full script is at the end of this note: `review_latency.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 review_latency.py prs.json
```

**Example output**

```text
ERR #412 31.2h 780L
6 of 42 breach
```

## Explained

### What it reads

The export is a JSON list, one object per pull request: number, author, created_at, first_review_at, merged_at, additions and deletions. Time to first review runs from created_at to first_review_at in hours. Size is additions plus deletions, which is the number a reviewer actually faces.

### What it does

The script parses the timestamps, computes the wait and the size, then flags a pull request as slow above twenty-four hours or large above four hundred changed lines. It lists every breach, prints a one-line summary and exits 1 when any threshold is crossed. No API token is involved: the export is the only input.

### How to use it

Run it on a weekday schedule or as a report step in CI: `python3 review_latency.py prs.json --first-review 24 --size 400`. The full script takes the thresholds as flags, prints a table and leaves the exit code for the pipeline. It only reads the export.

> **The honest caveat:** first review is not review quality, and a team can hit the target with a one-line approval. Pair the number with a read of the comments, or it becomes a target that gets gamed.

> **The lesson:** review latency is a queue, so make the queue visible before you ask anyone to go faster.

## In one line

> **A wait you cannot see is a default.** Time to first review is a service level, not a personality.

**Run it on export**

```bash
python3 review_latency.py prs.json
```

## Script: review_latency.py

Download: [scripts/review_latency.py](../scripts/review_latency.py)

```python
#!/usr/bin/env python3
"""Flag pull requests that wait too long for a first review.

Usage:
    python3 review_latency.py prs.json
    python3 review_latency.py prs.json --first-review 24 --size 400 --top 10

The export is a JSON list of objects with the keys number, author,
created_at, first_review_at, merged_at, additions and deletions. Timestamps
are ISO 8601; a trailing Z is accepted.

Time to first review runs from created_at to first_review_at, in hours. An
open PR with no review yet is measured to now and marked waiting; a merged
PR with no review is marked unreviewed and always counts as a breach. Size
is additions plus deletions. The report exits 1 when any PR breaches
--first-review hours or --size changed lines.

Cron (weekdays, 08:00):  0 8 * * 1-5  python3 review_latency.py prs.json
CI step: python3 review_latency.py prs.json   # non-zero fails the job

Exit codes: 0 clean, 1 a threshold is breached, 2 usage or input error.

By s0sta.com
"""
import argparse
import json
import sys
from datetime import datetime, timezone

DEFAULT_HOURS = 24.0
DEFAULT_SIZE = 400


def parse_time(value):
    """Parse an ISO 8601 timestamp, or return None for an empty value."""
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("timestamp is not a string: %r" % (value,))
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp


def hours_between(start, end):
    """Hours from start to end, or None when either is missing."""
    if start is None or end is None:
        return None
    return (end - start).total_seconds() / 3600.0


def read_export(path):
    """Read the JSON export and insist that it is a list."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("export must be a JSON list of pull requests")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Flag PRs with a slow first review or a large diff.")
    parser.add_argument("export", help="JSON export of pull requests")
    parser.add_argument("--first-review", type=float, default=DEFAULT_HOURS,
                        metavar="HOURS",
                        help="breach above this time to first review (24)")
    parser.add_argument("--size", type=int, default=DEFAULT_SIZE,
                        metavar="LINES",
                        help="breach above this many changed lines (400)")
    parser.add_argument("--top", type=int, default=10, metavar="N",
                        help="rows to print (10)")
    args = parser.parse_args(argv)

    if args.first_review <= 0 or args.size <= 0 or args.top < 1:
        print("ERROR thresholds and --top must be positive", file=sys.stderr)
        return 2

    try:
        prs = read_export(args.export)
    except (OSError, ValueError) as exc:
        print("ERROR cannot read %s: %s" % (args.export, exc), file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    rows = []
    breaches = 0
    for pr in prs:
        if not isinstance(pr, dict):
            print("ERROR every row must be a JSON object", file=sys.stderr)
            return 2
        number = pr.get("number", "?")
        try:
            created = parse_time(pr.get("created_at"))
            review = parse_time(pr.get("first_review_at"))
            merged = parse_time(pr.get("merged_at"))
            size = int(pr.get("additions") or 0) + int(pr.get("deletions") or 0)
        except (TypeError, ValueError) as exc:
            print("ERROR PR %s: %s" % (number, exc), file=sys.stderr)
            return 2
        if created is None:
            print("ERROR PR %s: created_at is required" % number, file=sys.stderr)
            return 2
        if size < 0:
            print("ERROR PR %s: negative size" % number, file=sys.stderr)
            return 2

        wait = hours_between(created, review)
        flags = []
        if review is None:
            if merged is None:
                wait = hours_between(created, now)
                if wait > args.first_review:
                    flags.append("waiting")
            else:
                flags.append("unreviewed")
        elif wait > args.first_review:
            flags.append("slow")
        if size > args.size:
            flags.append("large")
        if flags:
            breaches += 1
        rows.append((number, str(pr.get("author", "?")), wait, size,
                     ",".join(flags) or "-"))

    rows.sort(key=lambda row: -(row[2] if row[2] is not None else -1))
    print("%6s  %-14s %7s %6s  flags" % ("PR", "author", "wait h", "size"))
    for number, author, wait, size, flags in rows[: args.top]:
        shown = "-" if wait is None else "%.1f" % wait
        print("%6s  %-14s %7s %6s  %s"
              % (number, author[:14], shown, size, flags))
    if breaches:
        print("ERR %d of %d pull requests breach a threshold"
              % (breaches, len(prs)))
    else:
        print("OK %d pull requests within thresholds" % len(prs))
    return 1 if breaches else 0


if __name__ == "__main__":
    sys.exit(main())
```
