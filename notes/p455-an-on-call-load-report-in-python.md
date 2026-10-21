---
id: p455
title: "An on-call load report in Python"
slug: an-on-call-load-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [SRE, OnCall, Python, DevOps, Reliability]
source: "LinkedIn post P455 · DevOps series"
linkedin_date: 2029-08-23
design: code
script: oncall_load.py
---

# An on-call load report in Python

Every rota has one person who takes twice the pages and never says so. The pager log knows. This script turns it into a count per person per week, and fails when the load is not shared.

## Quick reference

The full script is at the end of this note: `oncall_load.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 oncall_load.py incidents.jsonl
```

**Example output**

```text
2026-W16  sam            8 pages   5 night
worst hour 03:00 UTC, 5 pages
```

## Explained

### What it does

It reads an incidents JSONL: one page per line, with paged_at, assignee and severity. For each person it counts pages by ISO week and how many landed between 22:00 and 07:00, then finds the hour of the day with the most pages. It prints the table and exits 1 when a person-week passes the threshold, eight by default.

### Why weeks

A night of four pages is noise. Five pages a week, every week, for one person is a retention problem that no retro will surface. ISO weeks put the Tuesday and the Sunday in the same bucket, so a bad rota shows up as a pattern rather than an anecdote.

### How to use it

`python3 oncall_load.py incidents.jsonl --threshold 6`, from cron on Monday morning or as a report step in CI. It exits 0 at or under the threshold, 1 over it, and 2 when the file is missing or a line will not parse. The full script is attached: standard library only, read-only.

> **The honest caveat:** a page count says nothing about difficulty. One SEV1 at 03:00 can cost more than ten SEV3 tickets, and the count treats them the same. Read the severities before you judge the rota.

> **The lesson:** measure the load before you argue about fairness.

## In one line

> **Share the pager, not the blame.** One person carrying every week is a rota bug, not a hero.

**Run it monday**

```bash
0 8 * * 1 python3 oncall_load.py
```

## Script: oncall_load.py

Download: [scripts/oncall_load.py](../scripts/oncall_load.py)

```python
#!/usr/bin/env python3
"""Report on-call pager load from an incidents JSONL file.

Usage:
    python3 oncall_load.py incidents.jsonl
    python3 oncall_load.py incidents.jsonl --threshold 6
    python3 oncall_load.py incidents.jsonl --night-start 21 --night-end 6
    python3 oncall_load.py incidents.jsonl --json
    python3 oncall_load.py --help

Each line is one page:

    {"paged_at": "2026-04-14T03:12:00+00:00", "assignee": "ana", "severity": "sev2"}

paged_at is ISO 8601; a trailing Z is accepted. assignee is the person who
was paged. severity is validated and counted in the JSON summary; it does not
change the per-person count. A page is a night page when its hour is at or
after --night-start (default 22) or before --night-end (default 7), in UTC.

The report gives pages per person per ISO week, the night pages per row, the
total night share and the hour of the day with the most pages. Ties go to the
earliest hour, because 03:00 is a worse rota than 15:00.

Exit codes: 0 under the threshold, 1 one person-week over it, 2 usage or
input error (bad JSON, missing field, bad timestamp). Read-only: the file is
opened for reading and never written.

Cron: 0 8 * * 1 python3 /opt/s0sta/oncall_load.py /var/tmp/incidents.jsonl
CI:   python3 oncall_load.py incidents.jsonl --threshold 6

By s0sta.com
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

DEFAULT_THRESHOLD = 8
DEFAULT_NIGHT_START = 22
DEFAULT_NIGHT_END = 7
FIELDS = ("paged_at", "assignee", "severity")


class InputError(Exception):
    """An input line or argument that cannot be used."""


def parse_when(value, where):
    """Parse an ISO 8601 timestamp into an aware UTC datetime."""
    text = str(value or "").strip()
    if not text:
        raise InputError("%s: paged_at is empty" % where)
    try:
        when = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise InputError("%s: bad paged_at %r (expected ISO 8601)"
                         % (where, value))
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


def load_pages(path):
    """Read the JSONL file and return one dict per page."""
    try:
        handle = open(path, "r", encoding="utf-8")
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    pages = []
    with handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            where = "%s line %d" % (path, number)
            try:
                row = json.loads(line)
            except ValueError:
                raise InputError("%s: not valid JSON" % where)
            if not isinstance(row, dict):
                raise InputError("%s: expected a JSON object" % where)
            missing = [name for name in FIELDS
                       if not str(row.get(name, "")).strip()]
            if missing:
                raise InputError("%s: missing %s"
                                 % (where, ", ".join(missing)))
            pages.append({
                "assignee": str(row["assignee"]).strip(),
                "severity": str(row["severity"]).strip(),
                "when": parse_when(row["paged_at"], where),
            })
    return pages


def is_night(hour, start, end):
    """True when hour falls in the night window, which may cross midnight."""
    if start > end:
        return hour >= start or hour < end
    return start <= hour < end


def build_report(pages, night_start, night_end):
    """Group pages by person and ISO week, and find the worst hour."""
    buckets = defaultdict(lambda: {"pages": 0, "night": 0})
    hours = Counter()
    for page in pages:
        when = page["when"]
        year, week, _day = when.isocalendar()
        key = (page["assignee"], year, week)
        buckets[key]["pages"] += 1
        hours[when.hour] += 1
        if is_night(when.hour, night_start, night_end):
            buckets[key]["night"] += 1
    rows = [{"assignee": who, "iso_year": year, "iso_week": week,
             "pages": counts["pages"], "night_pages": counts["night"]}
            for (who, year, week), counts in buckets.items()]
    rows.sort(key=lambda r: (r["iso_year"], r["iso_week"],
                             -r["pages"], r["assignee"]))
    worst = None
    if hours:
        hour, count = sorted(hours.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        worst = {"hour": hour, "pages": count}
    return rows, worst


def print_table(rows, worst, threshold):
    """Print the table and return the person-weeks over the threshold."""
    total = sum(r["pages"] for r in rows)
    night = sum(r["night_pages"] for r in rows)
    for row in rows:
        print("%04d-W%02d  %-12s %3d pages  %2d night"
              % (row["iso_year"], row["iso_week"], row["assignee"],
                 row["pages"], row["night_pages"]))
    share = 100.0 * night / total if total else 0.0
    print("")
    print("%d pages, %d at night (%.0f%%)" % (total, night, share))
    if worst:
        print("worst hour %02d:00 UTC, %d pages"
              % (worst["hour"], worst["pages"]))
    breaches = [r for r in rows if r["pages"] > threshold]
    for row in breaches:
        print("ALERT %s %d pages in %04d-W%02d (threshold %d)"
              % (row["assignee"], row["pages"], row["iso_year"],
                 row["iso_week"], threshold))
    return breaches


def build_parser():
    parser = argparse.ArgumentParser(
        description="Report pages per person per week from an incidents "
                    "JSONL file.",
        epilog="Exit 0 under the threshold, 1 over it, 2 usage or input "
               "error. By s0sta.com")
    parser.add_argument("path", help="incidents JSONL, one page per line")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                        metavar="N",
                        help="pages per person per week before exit 1 "
                             "(default %d)" % DEFAULT_THRESHOLD)
    parser.add_argument("--night-start", type=int, default=DEFAULT_NIGHT_START,
                        metavar="H",
                        help="first night hour, 0-23 (default %d)"
                             % DEFAULT_NIGHT_START)
    parser.add_argument("--night-end", type=int, default=DEFAULT_NIGHT_END,
                        metavar="H",
                        help="first day hour, 0-23 (default %d)"
                             % DEFAULT_NIGHT_END)
    parser.add_argument("--json", action="store_true",
                        help="print a JSON report instead of a table")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.threshold < 1:
            raise InputError("--threshold must be at least 1")
        for value, label in ((args.night_start, "--night-start"),
                             (args.night_end, "--night-end")):
            if not 0 <= value <= 23:
                raise InputError("%s must be 0-23, got %d" % (label, value))
        if args.night_start == args.night_end:
            raise InputError("night window is empty: --night-start equals "
                             "--night-end")
        pages = load_pages(args.path)
    except InputError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    rows, worst = build_report(pages, args.night_start, args.night_end)
    breaches = [r for r in rows if r["pages"] > args.threshold]
    total = len(pages)
    night = sum(r["night_pages"] for r in rows)
    by_severity = Counter(page["severity"] for page in pages)

    if args.json:
        print(json.dumps({
            "threshold": args.threshold,
            "night_window": [args.night_start, args.night_end],
            "total_pages": total,
            "night_pages": night,
            "worst_hour": worst,
            "by_severity": dict(sorted(by_severity.items())),
            "people": rows,
            "breaches": breaches,
        }, indent=2, sort_keys=True))
    else:
        print_table(rows, worst, args.threshold)
    return 1 if breaches else 0


if __name__ == "__main__":
    sys.exit(main())
```
