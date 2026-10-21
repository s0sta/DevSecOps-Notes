---
id: p762
title: "One page for the board"
slug: one-page-for-the-board
sections: [devsecops]
topic: "Python scripts"
tags: [Python, RiskManagement, CyberSecurity, CISO, GRC]
source: "LinkedIn post P762 · ASM series"
linkedin_date: 2031-08-10
design: code
script: risk_report.py
---

# One page for the board

The board asks one question: are we safer than last quarter? The security team sends a forty-page export and three colours, and the meeting moves on.

## Quick reference

The full script is at the end of this note: `risk_report.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 risk_report.py findings.json --previous prev.json
```

**Example output**

```text
RISK 76 up 14
2 critical, 2 KEV open
```

## Explained

### What it does

`risk_report.py` reads the current findings JSON and the export behind the last report. It prints open findings by severity, the known-exploited (KEV) count, mean and oldest age, the three assets with the most open findings, and a weighted score with every factor on the line. It exits 1 on an open KEV or a critical past 30 days, a policy line.

### On the screen

RISK 76 up 14, then 2 critical, 2 KEV open. The report prints the working: 10\*2 + 5\*5 + 2\*9 + 1\*3 + 5\*2 KEV.

### How to run it

`python3 risk_report.py findings.json --previous prev.json --today 2026-10-20`, before the pack. Exit 0 is clean, 1 is a board-level finding, 2 is a bad export.

### The fix

Send the page, not the export. The trend and the changed line carry the argument: a score that rose because two KEVs arrived is a sprint decision, not a colour.

### Prevention

Keep each month's export, same schema, in one directory. A report with no previous file is a snapshot pretending to be a trend.

> **The honest caveat:** the weights are a policy choice, not a standard. Change them and the trend changes, so freeze them for a year and write the choice down.

> **The lesson:** the board needs the delta and the reason, not more findings.

## In one line

> **A number the board can act on.** One page, one trend, and the factors behind the score.

**Send one page:** `risk_report.py f.json --previous p.json`

## Script: risk_report.py

Download: [scripts/risk_report.py](../scripts/risk_report.py)

```python
#!/usr/bin/env python3
"""risk_report.py - one page for the board, built from a findings export.

Reads a findings JSON export and, optionally, the export used for the previous
board report. It prints the open count by severity, the known-exploited (KEV)
count, the mean and oldest age, the three assets with the most open findings,
a weighted risk score with its factors, the trend against the previous report
and what changed since it.

Findings JSON is a list of objects:

    [{"id": "CVE-2026-1001", "severity": "critical", "asset": "web-01",
      "first_seen": "2026-07-15", "status": "open", "kev": true}]

severity is critical, high, medium or low. status is open or fixed. kev is
optional and defaults to false. Ages are counted to --today. A finding whose
first_seen is in the future is a bad export, not a negative age.

The risk score is a policy choice, not a standard: critical 10, high 5,
medium 2, low 1, plus 5 for each open KEV. The line prints every factor, so a
reader can reproduce the number without trusting the tool.

Accepted risk stays in the open count. A finding that is open in the export is
open on the page, whatever the exception register says.

Usage:
    python3 risk_report.py findings.json --previous last-month.json
    python3 risk_report.py findings.json --previous last-month.json --today 2026-10-20
    python3 risk_report.py findings.json --sla-days 30

Cron (Monday 06:00, before the board pack):
    0 6 * * 1 python3 /opt/s0sta/risk_report.py /var/lib/s0sta/findings.json --previous /var/lib/s0sta/findings.last.json

Exit codes: 0 no open KEV and no critical older than --sla-days, 1 either is
present, 2 usage or a findings export that is missing, unreadable, invalid,
duplicated or inconsistent.

Read-only: reads the exports and prints. It writes nothing and makes no
network call.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import datetime as dt
import json
import sys
from collections import Counter

SEVERITIES = ("critical", "high", "medium", "low")
WEIGHTS = {"critical": 10, "high": 5, "medium": 2, "low": 1}
KEV_POINTS = 5


class InputError(Exception):
    """An export that cannot be turned into a board page."""


def parse_day(text, label):
    """Return a date from an ISO string, or raise InputError."""
    if not isinstance(text, str):
        raise InputError("%s is not an ISO date" % label)
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        raise InputError("%s is not an ISO date: %s" % (label, text))


def load_findings(path, today):
    """Read and validate one findings export. Return normalised records."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, list):
        raise InputError("%s must contain a JSON list of findings" % path)

    rows = []
    seen = set()
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise InputError("%s: finding %d is not an object" % (path, number))
        finding_id = item.get("id")
        if not isinstance(finding_id, str) or not finding_id.strip():
            raise InputError("%s: finding %d has no id" % (path, number))
        finding_id = finding_id.strip()
        if finding_id in seen:
            raise InputError("%s: duplicate finding id %s" % (path, finding_id))
        seen.add(finding_id)
        severity = item.get("severity")
        if severity not in WEIGHTS:
            raise InputError("%s: %s has an unknown severity %r"
                             % (path, finding_id, severity))
        asset = item.get("asset")
        if not isinstance(asset, str) or not asset.strip():
            raise InputError("%s: %s has no asset" % (path, finding_id))
        status = item.get("status")
        if status not in ("open", "fixed"):
            raise InputError("%s: %s has an unknown status %r"
                             % (path, finding_id, status))
        kev = item.get("kev", False)
        if not isinstance(kev, bool):
            raise InputError("%s: %s kev must be true or false"
                             % (path, finding_id))
        first_seen = parse_day(item.get("first_seen"),
                               "%s: %s first_seen" % (path, finding_id))
        if first_seen > today:
            raise InputError("%s: %s starts in the future" % (path, finding_id))
        rows.append({
            "id": finding_id,
            "severity": severity,
            "asset": asset.strip(),
            "status": status,
            "kev": kev,
            "first_seen": first_seen,
        })
    return rows


def summarise(rows, today):
    """Return the board numbers for one export."""
    open_rows = [row for row in rows if row["status"] == "open"]
    counts = Counter(row["severity"] for row in open_rows)
    ages = [(today - row["first_seen"]).days for row in open_rows]
    kev_open = sum(row["kev"] for row in open_rows)
    kev_all = sum(row["kev"] for row in rows)
    score = sum(WEIGHTS[s] * counts[s] for s in SEVERITIES) + KEV_POINTS * kev_open
    factors = ["%d*%d" % (WEIGHTS[s], counts[s]) for s in SEVERITIES]
    factors.append("%d*%d KEV" % (KEV_POINTS, kev_open))
    top = Counter(row["asset"] for row in open_rows)
    return {
        "open": open_rows,
        "counts": counts,
        "total": len(open_rows),
        "kev_open": kev_open,
        "kev_all": kev_all,
        "mean_age": int(round(sum(ages) / len(ages))) if ages else 0,
        "oldest": max(ages) if ages else 0,
        "score": score,
        "factors": " + ".join(factors),
        "top": sorted(top.items(), key=lambda item: (-item[1], item[0]))[:3],
    }


def trend_line(now, before):
    """Return the trend sentence for two summaries."""
    if before is None:
        return "TREND none, no previous report"
    delta = now["score"] - before["score"]
    word = "up" if delta > 0 else "down" if delta < 0 else "flat"
    return "TREND %s %d since last report" % (word, abs(delta))


def changed_line(now, before):
    """Return the change sentence for two summaries."""
    if before is None:
        return "CHANGED none, no previous report"
    parts = []
    for severity in SEVERITIES:
        delta = now["counts"][severity] - before["counts"][severity]
        if delta:
            parts.append("%+d %s" % (delta, severity))
    now_ids = {row["id"] for row in now["open"]}
    before_ids = {row["id"] for row in before["open"]}
    new_ids = now_ids - before_ids
    closed_ids = before_ids - now_ids
    if new_ids:
        parts.append("new %d" % len(new_ids))
    if closed_ids:
        parts.append("closed %d" % len(closed_ids))
    return "CHANGED " + (", ".join(parts) if parts else "none")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a one-page board summary from a findings export.")
    parser.add_argument("findings", help="current findings JSON export")
    parser.add_argument("--previous", help="findings export used for the last report")
    parser.add_argument("--today", help="ISO date for the report, default today")
    parser.add_argument("--sla-days", type=int, default=30,
                        help="days a critical finding may stay open (default 30)")
    args = parser.parse_args(argv)
    if args.sla_days < 0:
        parser.error("--sla-days must be zero or more")

    try:
        today = parse_day(args.today, "--today") if args.today else dt.date.today()
        rows = load_findings(args.findings, today)
        previous = load_findings(args.previous, today) if args.previous else None
    except InputError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    now = summarise(rows, today)
    before = summarise(previous, today) if previous is not None else None

    print("OPEN %d total: %s" % (
        now["total"], ", ".join("%d %s" % (now["counts"][s], s) for s in SEVERITIES)))
    print("KEV %d open of %d known" % (now["kev_open"], now["kev_all"]))
    print("AGE mean %d days, oldest %d days" % (now["mean_age"], now["oldest"]))
    print("TOP " + (", ".join("%s %d" % item for item in now["top"]) or "none"))
    print("RISK %d = %s" % (now["score"], now["factors"]))
    print(trend_line(now, before))
    print(changed_line(now, before))

    old_critical = [row for row in now["open"]
                    if row["severity"] == "critical"
                    and (today - row["first_seen"]).days > args.sla_days]
    if now["kev_open"] or old_critical:
        print("FINDING %d KEV open, %d critical past %d days"
              % (now["kev_open"], len(old_critical), args.sla_days))
        return 1
    print("OK no open KEV, no critical past %d days" % args.sla_days)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
