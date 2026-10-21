---
id: p466
title: "A CI cost report in Python"
slug: a-ci-cost-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, CICD, FinOps, DevOps, CloudComputing]
source: "LinkedIn post P466 · DevOps series"
linkedin_date: 2029-09-18
design: code
script: ci_cost.py
---

# A CI cost report in Python

The CI bill arrives once a month, long after the pull request that doubled the minutes. Projecting it from a usage export turns a surprise into a weekly number.

## Quick reference

The full script is at the end of this note: `ci_cost.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 ci_cost.py usage.json --budget 200
```

**Example output**

```text
api                 96.00
ERR month 212.57
```

## Explained

### What it reads

The export is a JSON list, one object per repository: repo, minutes and price per minute. If a row omits the price, the script uses the rate passed on the command line. Spend is minutes times price, which is the part of the bill a team controls.

### What it does

It ranks repositories by spend, totals the month to date, and projects the full month from the days elapsed. Then it compares the projection with the budget and exits 1 when the projection is over. A clean run exits 0; a bad export exits 2, which is not the same as over budget. The top rows show which repository to fix first.

### How to use it

Run it daily from cron or as a scheduled job: `python3 ci_cost.py usage.json --budget 400`. The full script accepts `--price`, `--day`, `--days` and `--top`, so a mid-month run or a short month is not a special case. It reads one file and writes nothing.

> **The honest caveat:** minutes are not the whole bill. Storage, larger runners, and Windows or macOS minutes are priced differently, so the projection is a floor, not an invoice.

> **The lesson:** a budget you cannot see is a budget you will exceed.

## In one line

> **Minutes are money now.** A budget nobody projects is a surprise in December.

**Set the budget**

```bash
python3 ci_cost.py usage.json --budget 400
```

## Script: ci_cost.py

Download: [scripts/ci_cost.py](../scripts/ci_cost.py)

```python
#!/usr/bin/env python3
"""Rank CI spend by repository and fail when the month is over budget.

Usage:
    python3 ci_cost.py usage.json --budget 400
    python3 ci_cost.py usage.json --budget 400 --price 0.008 --top 5

The export is a JSON list of objects with the keys repo, minutes and,
optionally, price_per_minute. A row's own price wins; --price is the
fallback for rows that omit it. Spend is minutes times price. The month is
projected from --day and --days (defaults: today's day of the month and the
length of the current month), and the report exits 1 when the projection is
over --budget.

The export should cover the current month to date. Prices differ by runner
size and operating system, so pass the rate on your own bill.

Cron (daily, 07:30):  30 7 * * *  python3 ci_cost.py usage.json --budget 400
CI gate: python3 ci_cost.py usage.json --budget 400   # non-zero fails the job

Exit codes: 0 clean, 1 the budget is breached, 2 usage or input error.

By s0sta.com
"""
import argparse
import calendar
import json
import sys
from datetime import date

DEFAULT_PRICE = 0.008


def read_usage(path):
    """Read the JSON usage export and insist that it is a list."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("export must be a JSON list of usage rows")
    return data


def main(argv=None):
    today = date.today()
    parser = argparse.ArgumentParser(
        description="Rank CI spend by repo and project the month.")
    parser.add_argument("usage", help="JSON export of CI usage rows")
    parser.add_argument("--budget", type=float, required=True, metavar="USD",
                        help="monthly budget in dollars")
    parser.add_argument("--price", type=float, default=DEFAULT_PRICE,
                        metavar="USD",
                        help="fallback price per minute (0.008)")
    parser.add_argument("--day", type=int, default=today.day, metavar="N",
                        help="day of the month covered by the export")
    parser.add_argument("--days", type=int,
                        default=calendar.monthrange(today.year, today.month)[1],
                        metavar="N", help="days in the month")
    parser.add_argument("--top", type=int, default=10, metavar="N",
                        help="rows to print (10)")
    args = parser.parse_args(argv)

    if args.budget < 0:
        print("ERROR --budget cannot be negative", file=sys.stderr)
        return 2
    if args.price <= 0:
        print("ERROR --price must be positive", file=sys.stderr)
        return 2
    if not 1 <= args.day <= 31 or not 28 <= args.days <= 31:
        print("ERROR --day must be 1-31 and --days 28-31", file=sys.stderr)
        return 2
    if args.day > args.days:
        print("ERROR --day cannot exceed --days", file=sys.stderr)
        return 2
    if args.top < 1:
        print("ERROR --top must be positive", file=sys.stderr)
        return 2

    try:
        usage = read_usage(args.usage)
    except (OSError, ValueError) as exc:
        print("ERROR cannot read %s: %s" % (args.usage, exc), file=sys.stderr)
        return 2

    spend = []
    for row in usage:
        if not isinstance(row, dict):
            print("ERROR every row must be a JSON object", file=sys.stderr)
            return 2
        repo = row.get("repo")
        if not isinstance(repo, str) or not repo:
            print("ERROR every row needs a repo name", file=sys.stderr)
            return 2
        try:
            minutes = float(row.get("minutes", 0))
            price = float(row.get("price_per_minute", args.price))
        except (TypeError, ValueError) as exc:
            print("ERROR %s: %s" % (repo, exc), file=sys.stderr)
            return 2
        if minutes < 0 or price <= 0:
            print("ERROR %s: minutes >= 0 and price > 0" % repo,
                  file=sys.stderr)
            return 2
        spend.append((repo, minutes, price, minutes * price))

    total = sum(row[3] for row in spend)
    projected = total / args.day * args.days

    spend.sort(key=lambda row: -row[3])
    print("%-20s %8s %8s %10s" % ("repo", "minutes", "rate", "spend"))
    for repo, minutes, price, cost in spend[: args.top]:
        print("%-20s %8.0f %8.4f %10.2f" % (repo, minutes, price, cost))
    print("spend to date %.2f, projected %.2f, budget %.2f"
          % (total, projected, args.budget))
    if projected > args.budget:
        print("ERR projection %.2f is over budget %.2f"
              % (projected, args.budget))
        return 1
    print("OK projection %.2f is within budget %.2f"
          % (projected, args.budget))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
