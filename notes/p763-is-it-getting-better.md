---
id: p763
title: "Is it getting better?"
slug: is-it-getting-better
sections: [devsecops]
topic: "Python scripts"
tags: [Python, VulnerabilityManagement, Metrics, CyberSecurity, DevOps]
source: "LinkedIn post P763 · ASM series"
linkedin_date: 2031-08-12
design: code
script: trend_report.py
---

# Is it getting better?

The monthly slide says 1,842 findings closed. It does not say 2,100 opened, so the backlog grew and the room applauds.

## Quick reference

The full script is at the end of this note: `trend_report.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 trend_report.py history.json
```

**Example output**

```text
NET +11, closure 22%
WORSENING two periods up
```

## Explained

### What it does

`trend_report.py` reads a JSON history of scan snapshots. Each period prints the open count, net flow (opened minus closed), and the closure rate with its denominator: closed divided by the findings in play, which is the open count at the start plus everything opened. The start count comes from mass balance; an inconsistent history is rejected. It also prints time-to-close, weighted by closures, and flags a closure drop of five points, a backlog that grew two periods running, or critical plus high rising.

### On the screen

NET +11, closure 22%, then WORSENING two periods up. Behind it: 33 days mean, 186 closures.

### How to run it

`python3 trend_report.py history.json`, after the scans land. Exit 0 is no signal, 1 is at least one, 2 is a broken history.

### The fix

Put net flow and the denominator beside the closures on the same slide. When the backlog has grown for two periods, stop adding scanners and close the oldest severe findings.

### Prevention

Append one snapshot after every scan cycle, same fields. A missing month is a gap; a hand-edited month is worse.

> **The honest caveat:** these are counts, not cohorts; the five-point line is policy, not a standard. A finding opened in March and closed in September counts twice, and the mean hides the slow tail.

> **The lesson:** a closure count is a numerator; a programme is a denominator.

## In one line

> **Direction beats a single number.** Net flow and a denominator turn a count into a direction.

**Check the flow**

```bash
python3 trend_report.py history.json
```

## Script: trend_report.py

Download: [scripts/trend_report.py](../scripts/trend_report.py)

```python
#!/usr/bin/env python3
"""trend_report.py - is the vulnerability programme getting better?

Reads a history of scan snapshots and prints, per period, the open count, the
net flow (opened minus closed) and the closure rate with the denominator that
produced it. It then prints the window totals, the time-to-close weighted by
closures, and flags a worsening trend.

Snapshots JSON is a list in date order:

    [{"date": "2026-07-31", "critical": 12, "high": 44, "medium": 74,
      "low": 22, "opened": 55, "closed": 43, "mean_days_to_close": 32}]

The four severity counts are the findings open at the end of the period.
opened and closed are the flows during it. The open count at the start is
reconstructed by mass balance:

    open_start = open_end - opened + closed

The closure rate is closed / (open_start + opened): the share of everything
in play during the period that was closed. A rate without that denominator is
a number about the team, not about the backlog.

The trend is a finding when any of these is true:
  - the latest closure rate is --drop points below the previous period;
  - net flow is positive in each of the last two periods;
  - critical plus high is higher than in the previous period.
Those thresholds are a policy choice. The printed factors let you argue with
them.

Usage:
    python3 trend_report.py history.json
    python3 trend_report.py history.json --drop 3

Cron (daily 07:00, after the scan exports land):
    0 7 * * * python3 /opt/s0sta/trend_report.py /var/lib/s0sta/history.json

CI (fail the report job when the trend worsens):
    python3 trend_report.py history.json || exit 1

Exit codes: 0 no worsening signal, 1 at least one signal, 2 usage or a history
that is missing, unreadable, invalid, out of order or inconsistent.

Read-only: reads the history and prints. It writes nothing and makes no
network call.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import datetime as dt
import json
import sys

SEVERITIES = ("critical", "high", "medium", "low")


class InputError(Exception):
    """A history that cannot be turned into a trend."""


def parse_day(text, label):
    """Return a date from an ISO string, or raise InputError."""
    if not isinstance(text, str):
        raise InputError("%s is not an ISO date" % label)
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        raise InputError("%s is not an ISO date: %s" % (label, text))


def count_field(snapshot, key, number):
    """Return a non-negative integer field, or raise InputError."""
    value = snapshot.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InputError("snapshot %d: %s must be a non-negative integer"
                         % (number, key))
    return value


def load_history(path):
    """Read and validate the snapshots. Return a list of metric dicts."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, list):
        raise InputError("%s must contain a JSON list of snapshots" % path)
    if len(doc) < 2:
        raise InputError("%s needs at least two snapshots to show a trend" % path)

    rows = []
    previous_day = None
    for number, snapshot in enumerate(doc, 1):
        if not isinstance(snapshot, dict):
            raise InputError("snapshot %d is not an object" % number)
        day = parse_day(snapshot.get("date"), "snapshot %d date" % number)
        if previous_day is not None and day <= previous_day:
            raise InputError("snapshot %d is not after the one before it" % number)
        previous_day = day
        opened = count_field(snapshot, "opened", number)
        closed = count_field(snapshot, "closed", number)
        mean = snapshot.get("mean_days_to_close")
        if isinstance(mean, bool) or not isinstance(mean, (int, float)) or mean < 0:
            raise InputError("snapshot %d: mean_days_to_close must be a "
                             "non-negative number" % number)
        counts = {key: count_field(snapshot, key, number) for key in SEVERITIES}
        open_end = sum(counts.values())
        open_start = open_end - opened + closed
        if open_start < 0:
            raise InputError("snapshot %d: opened and closed do not fit the "
                             "open counts" % number)
        denominator = open_start + opened
        rows.append({
            "date": day,
            "counts": counts,
            "open_end": open_end,
            "open_start": open_start,
            "opened": opened,
            "closed": closed,
            "net": opened - closed,
            "denominator": denominator,
            "rate": (closed / denominator) if denominator else None,
            "mean": float(mean),
            "severe": counts["critical"] + counts["high"],
        })
    return rows


def rate_text(rate):
    """Format a closure rate, or n/a when nothing was in play."""
    return "n/a" if rate is None else "%d%%" % round(100 * rate)


def worsening(rows, drop):
    """Return a list of reasons the latest period is worse."""
    latest, previous = rows[-1], rows[-2]
    reasons = []
    if latest["rate"] is not None and previous["rate"] is not None:
        points = round(100 * (previous["rate"] - latest["rate"]))
        if points >= drop:
            reasons.append("closure down %d pts" % points)
    if rows[-1]["net"] > 0 and rows[-2]["net"] > 0:
        reasons.append("backlog up 2 periods")
    if latest["severe"] > previous["severe"]:
        reasons.append("severe up %d" % (latest["severe"] - previous["severe"]))
    return reasons


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Show the vulnerability trend and flag a worsening period.")
    parser.add_argument("history", help="JSON list of scan snapshots in date order")
    parser.add_argument("--drop", type=int, default=5,
                        help="closure-rate drop in points that counts as worse "
                             "(default 5)")
    args = parser.parse_args(argv)
    if not 0 <= args.drop <= 100:
        parser.error("--drop must be between 0 and 100")

    try:
        rows = load_history(args.history)
    except InputError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    for row in rows:
        print("%s open %d, net %+d, closed %d/%d (%s)" % (
            row["date"], row["open_end"], row["net"], row["closed"],
            row["denominator"], rate_text(row["rate"])))

    total_closed = sum(row["closed"] for row in rows)
    total_denominator = sum(row["denominator"] for row in rows)
    window_rate = (total_closed / total_denominator) if total_denominator else None
    weighted_mean = (sum(row["closed"] * row["mean"] for row in rows)
                     / total_closed) if total_closed else None
    print("WINDOW %s to %s, net %+d, open %d -> %d" % (
        rows[0]["date"], rows[-1]["date"],
        sum(row["net"] for row in rows), rows[0]["open_end"], rows[-1]["open_end"]))
    mean_text = ("n/a" if weighted_mean is None
                 else "%d days" % round(weighted_mean))
    print("CLOSE %s latest, %s window, mean %s over %d closures" % (
        rate_text(rows[-1]["rate"]), rate_text(window_rate),
        mean_text, total_closed))

    reasons = worsening(rows, args.drop)
    if reasons:
        print("WORSENING " + ", ".join(reasons))
        return 1
    print("OK closure stable or improving, backlog not growing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
