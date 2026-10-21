---
id: p764
title: "What the scanner never saw"
slug: what-the-scanner-never-saw
sections: [devsecops]
topic: "Python scripts"
tags: [Python, AttackSurface, VulnerabilityManagement, CyberSecurity, DevSecOps]
source: "LinkedIn post P764 · ASM series"
linkedin_date: 2031-08-14
design: code
script: coverage_report.py
---

# What the scanner never saw

The coverage slide says 94%. The number is scans sent divided by the assets the scanner already knew about, and the database nobody added to the inventory is invisible.

## Quick reference

The full script is at the end of this note: `coverage_report.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 coverage_report.py inv.json scans.json
```

**Example output**

```text
GAP 2 assets with a tool gap
CRITICAL db-02
```

## Explained

### What it does

`coverage_report.py` joins the asset inventory with the scan records. For each required tool it looks for a successful scan inside the window; a failed scan is an attempt, not a result. It prints scanned and tool-complete counts, lists the gaps, and names scanned assets that are not in the inventory at all. Exit 1 when a gap reaches `--fail-on`, critical by default; that line is policy.

### On the screen

GAP 2 assets with a tool gap, then CRITICAL db-02. Behind it, 9 of 10 assets were scanned and 8 had every tool; lab-07 was scanned but unknown to the inventory.

### How to run it

`python3 coverage_report.py inventory.json scans.json --tools` trivy,osquery `--days 30`. Exit 0 is no gap at the line, 1 is at least one, 2 is a bad export.

### The fix

Add db-02 to the inventory and the scan scope, then rerun. Send lab-07 to the CMDB owner: an asset you cannot name is not covered.

### Prevention

Run the join weekly and treat a missing critical asset as an incident. The inventory is the denominator, so keep it current.

> **The honest caveat:** coverage proves a scan ran, not that it was configured to find anything. A scanner with stale plugins covers the asset and misses the CVE.

> **The lesson:** a scanner can only report on what it was pointed at.

## In one line

> **Unscanned is not clean.** A clean report over half the estate is not a clean report.

**Find the blind**

```bash
python3 coverage_report.py inv scans
```

## Script: coverage_report.py

Download: [scripts/coverage_report.py](../scripts/coverage_report.py)

```python
#!/usr/bin/env python3
"""coverage_report.py - what the scanner never saw.

Compares the asset inventory with the scan records and reports the assets that
were never scanned, the assets missing one of the required tools, and the
scanned assets that are not in the inventory at all. A clean report over half
the estate is not a clean report.

Inventory JSON is a list of assets:

    [{"asset": "web-01", "criticality": "critical"},
     {"asset": "lab-01", "criticality": "low"}]

Scans JSON is a list of scan records:

    [{"asset": "web-01", "tool": "trivy", "date": "2026-10-12",
      "status": "ok"},
     {"asset": "web-01", "tool": "osquery", "date": "2026-10-12",
      "status": "ok"}]

status is ok or failed. Only an ok scan inside the --days window counts as
coverage; a failed scan is an attempt, not a result. The required tools are a
comma-separated list: --tools trivy,osquery by default.

The exit code is a policy decision. --fail-on critical (the default) fails
only when a critical asset has a gap; --fail-on high tightens it. Gaps below
that line are still printed, because a high asset nobody scanned is not a
detail.

Usage:
    python3 coverage_report.py inventory.json scans.json
    python3 coverage_report.py inventory.json scans.json --today 2026-10-20
    python3 coverage_report.py inventory.json scans.json --days 7 --fail-on high

Cron (daily 06:15, before the morning stand-up):
    15 6 * * * python3 /opt/s0sta/coverage_report.py /etc/s0sta/assets.json /var/lib/s0sta/scans.json

CI (block a release when a critical asset is blind):
    python3 coverage_report.py assets.json scans.json || exit 1

Exit codes: 0 no gap at or above --fail-on, 1 at least one, 2 usage or an
inventory or scan export that is missing, unreadable, invalid or inconsistent.

Read-only: reads the two exports and prints. It writes nothing and makes no
network call.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import datetime as dt
import json
import sys

RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
DEFAULT_TOOLS = "trivy,osquery"


class InputError(Exception):
    """An export that cannot be compared with the other one."""


def parse_day(text, label):
    """Return a date from an ISO string, or raise InputError."""
    if not isinstance(text, str):
        raise InputError("%s is not an ISO date" % label)
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        raise InputError("%s is not an ISO date: %s" % (label, text))


def load_inventory(path):
    """Read the inventory. Return a list of (asset, criticality)."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, list) or not doc:
        raise InputError("%s must contain a non-empty JSON list of assets" % path)

    assets = []
    seen = set()
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise InputError("%s: asset %d is not an object" % (path, number))
        name = item.get("asset")
        if not isinstance(name, str) or not name.strip():
            raise InputError("%s: asset %d has no name" % (path, number))
        name = name.strip()
        if name in seen:
            raise InputError("%s: duplicate asset %s" % (path, name))
        seen.add(name)
        criticality = item.get("criticality")
        if criticality not in RANK:
            raise InputError("%s: %s has an unknown criticality %r"
                             % (path, name, criticality))
        assets.append((name, criticality))
    return assets


def load_scans(path, today, inventory):
    """Read the scan records. Return (ok scans, unknown assets)."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, list):
        raise InputError("%s must contain a JSON list of scan records" % path)

    scans = []
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise InputError("%s: scan %d is not an object" % (path, number))
        asset = item.get("asset")
        if not isinstance(asset, str) or not asset.strip():
            raise InputError("%s: scan %d has no asset" % (path, number))
        tool = item.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            raise InputError("%s: scan %d has no tool" % (path, number))
        status = item.get("status")
        if status not in ("ok", "failed"):
            raise InputError("%s: scan %d has an unknown status %r"
                             % (path, number, status))
        day = parse_day(item.get("date"), "%s: scan %d date" % (path, number))
        if day > today:
            raise InputError("%s: scan %d is dated in the future"
                             % (path, number))
        scans.append({
            "asset": asset.strip(),
            "tool": tool.strip(),
            "status": status,
            "date": day,
        })

    unknown = sorted({scan["asset"] for scan in scans
                      if scan["asset"] not in {a for a, _ in inventory}})
    return scans, unknown


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare an asset inventory with scan coverage.")
    parser.add_argument("inventory", help="JSON list of assets")
    parser.add_argument("scans", help="JSON list of scan records")
    parser.add_argument("--tools", default=DEFAULT_TOOLS,
                        help="required tools, comma separated (default %s)"
                             % DEFAULT_TOOLS)
    parser.add_argument("--days", type=int, default=30,
                        help="coverage window in days (default 30)")
    parser.add_argument("--today", help="ISO date for the window, default today")
    parser.add_argument("--fail-on", choices=("critical", "high", "medium", "low"),
                        default="critical",
                        help="criticality at which a gap fails the job "
                             "(default critical)")
    args = parser.parse_args(argv)
    if args.days < 1:
        parser.error("--days must be at least 1")

    tools = []
    for tool in args.tools.split(","):
        tool = tool.strip()
        if tool and tool not in tools:
            tools.append(tool)
    if not tools:
        parser.error("--tools needs at least one tool name")

    try:
        today = parse_day(args.today, "--today") if args.today else dt.date.today()
        inventory = load_inventory(args.inventory)
        scans, unknown = load_scans(args.scans, today, inventory)
    except InputError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    cutoff = today - dt.timedelta(days=args.days)
    covered = {asset: set() for asset, _ in inventory}
    for scan in scans:
        if (scan["status"] == "ok" and scan["date"] >= cutoff
                and scan["asset"] in covered):
            covered[scan["asset"]].add(scan["tool"])

    scanned = sum(1 for asset, _ in inventory if covered[asset])
    complete = sum(1 for asset, _ in inventory
                   if covered[asset] >= set(tools))
    print("COVERAGE %d/%d assets scanned, %d/%d with every tool (%d days: %s)"
          % (scanned, len(inventory), complete, len(inventory), args.days,
             ", ".join(tools)))

    gaps = []
    for asset, criticality in inventory:
        missing = [tool for tool in tools if tool not in covered[asset]]
        if missing:
            gaps.append((asset, criticality, missing))

    print("GAP %d assets with a tool gap" % len(gaps))
    for asset, criticality, _missing in gaps:
        if RANK[criticality] >= RANK[args.fail_on]:
            print("%s %s" % (criticality.upper(), asset))
    for asset, criticality, missing in gaps:
        if RANK[criticality] < RANK[args.fail_on]:
            print("TOOL %s: %s" % (asset, ", ".join(missing)))
    if unknown:
        print("NOTE %s scanned but not in inventory" % ", ".join(unknown))

    failing = [gap for gap in gaps if RANK[gap[1]] >= RANK[args.fail_on]]
    if failing:
        print("FAIL %d gap%s at or above %s"
              % (len(failing), "" if len(failing) == 1 else "s", args.fail_on))
        return 1
    if gaps:
        print("OK no gap at or above %s (%d below the line)"
              % (args.fail_on, len(gaps)))
    else:
        print("OK every asset has every required tool in the window")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
