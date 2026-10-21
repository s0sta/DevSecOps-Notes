---
id: p755
title: "Give the owner a packet, not a dashboard"
slug: give-the-owner-a-packet-not-a-dashboard
sections: [devsecops]
topic: "Python scripts"
tags: [VulnerabilityManagement, SRE, Python, Automation, CyberSecurity]
source: "LinkedIn post P755 · ASM series"
linkedin_date: 2031-07-24
design: code
script: owner_brief.py
---

# Give the owner a packet, not a dashboard

The owner opens the dashboard, filters to their service, and gets 84 rows with no order, no fix version and no due date. They close the tab, and the findings stay open.

## Quick reference

The full script is at the end of this note: `owner_brief.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 owner_brief.py findings.json --owner platform --today 2026-10-21
```

**Example output**

```text
VERIFY python3 rescan_diff.py before.json after.json
FAIL 1 overdue, 2 due this week
```

## Explained

### What it does

`owner_brief.py` reads a findings export and one owner name. It keeps that owner's open rows, sorts them by severity, then due date, then id, and prints a packet: the counts, the overdue rows, the top five with asset, severity, fix version and due date, a title and evidence link each, and one command that proves the fix. It exits 1 when anything is overdue.

### What the screen shows

The thirteen lines filter by owner, turn the due dates into overdue and due-this-week counts, and end with VERIFY `python3 rescan_diff.py before.json after.json` and FAIL 1 overdue, 2 due this week.

### How to run it

`python3 owner_brief.py findings.json --owner platform --today 2026-10-21 > brief.txt`. Run it per owner every Monday and paste it into the ticket.

### The fix

Send the packet. The owner replies with a date or an exception, and both beat a dashboard nobody opens.

### Prevention

Keep one template, one owner per packet, and the verify command at the end. A packet that fits in a message gets read.

> **The honest caveat:** the brief repeats the export, so a wrong due date or severity is wrong in the packet too.

> **The lesson:** an owner needs a short list they can finish.

## In one line

> **A packet, not a dashboard.** One owner, five items, one command that proves them.

**Build a brief**

```bash
python3 owner_brief.py f.json --owner api
```

## Script: owner_brief.py

Download: [scripts/owner_brief.py](../scripts/owner_brief.py)

```python
#!/usr/bin/env python3
"""Build a remediation brief for one owner from a findings export.

Reads a findings export as JSON:

    {"findings": [
        {"id": "F-2001", "asset": "api-01", "service": "api",
         "owner": "platform", "severity": "critical", "title": "request smuggling",
         "cvss": 9.8, "fix_version": "1.24.0", "due": "2026-10-24",
         "evidence": "https://scanner.local/f/F-2001"},
        ...]}

The output is a packet, not a dashboard: one owner, the counts that matter,
the overdue items, the top items with a fix version, a due date and an
evidence link each, and one command that proves the fix afterwards. It fits in
a chat message, a ticket or the body of an email.

Items are ordered by severity, then due date, then id. An item with no due
date sorts last and prints as due none. --top limits the list; the counts and
the overdue line still cover every open finding for the owner.

Usage:
    python3 owner_brief.py findings.json --owner platform
    python3 owner_brief.py findings.json --owner platform --top 3
    python3 owner_brief.py findings.json --owner platform --today 2026-10-21
    python3 owner_brief.py findings.json --owner platform > brief.txt

Exit codes: 0 no item overdue, 1 at least one item overdue, 2 usage or
invalid input.

CI (post the brief to the owner's channel every Monday):
    python3 owner_brief.py findings.json --owner platform --top 5

Cron (daily at 07:00, one brief per owner):
    0 7 * * * python3 /opt/s0sta/owner_brief.py /exports/findings.json --owner platform

The script is read-only: one JSON file, no scanner, no API calls, no writes.
Redirect the output if you want a file. The brief repeats the export: it does
not re-score a finding, and a wrong due date in the export is a wrong due date
in the packet. The verify command at the end is the rescan diff from this
series; run it with the same two exports the finding came from.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys
from datetime import date

RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
ORDER = ("critical", "high", "medium", "low")
DUE_SOON_DAYS = 7


class BriefError(Exception):
    """Anything that should end the run with exit code 2."""


def load_json(source, label):
    """Read JSON from a path, or stdin when source is '-'."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise BriefError("cannot read %s: %s" % (label, exc))
    except ValueError as exc:
        raise BriefError("%s is not valid JSON: %s" % (label, exc))


def text_field(item, key, label):
    """Return a stripped string field, treating null as empty."""
    value = item.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise BriefError("%s must be a string" % label)
    return value.strip()


def parse_day(value, label):
    """Parse a YYYY-MM-DD date or return None when it is absent."""
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise BriefError("%s must be a YYYY-MM-DD string" % label)
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise BriefError("%s is not a YYYY-MM-DD date: %r" % (label, value))


def read_findings(doc):
    """Validate the export and return one row per finding."""
    if isinstance(doc, dict):
        doc = doc.get("findings")
    if not isinstance(doc, list):
        raise BriefError("the export must be a list or an object with findings")
    rows = []
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise BriefError("finding %d is not an object" % number)
        fid = item.get("id") or "finding %d" % number
        if not isinstance(fid, str):
            raise BriefError("finding %d id must be a string" % number)
        fid = fid.strip()
        asset = text_field(item, "asset", "%s asset" % fid)
        owner = text_field(item, "owner", "%s owner" % fid)
        severity = text_field(item, "severity", "%s severity" % fid).lower()
        if not asset:
            raise BriefError("%s needs an asset" % fid)
        if severity not in RANK:
            raise BriefError("%s has unknown severity %r" % (fid, severity))
        cvss = item.get("cvss")
        if cvss is not None and (isinstance(cvss, bool)
                                 or not isinstance(cvss, (int, float))):
            raise BriefError("%s cvss must be a number" % fid)
        rows.append({
            "id": fid,
            "asset": asset,
            "service": text_field(item, "service", "%s service" % fid),
            "owner": owner,
            "severity": severity,
            "cvss": cvss,
            "title": text_field(item, "title", "%s title" % fid),
            "fix": text_field(item, "fix_version", "%s fix_version" % fid),
            "evidence": text_field(item, "evidence", "%s evidence" % fid),
            "due": parse_day(item.get("due"), "%s due" % fid),
        })
    return rows


def sort_key(row):
    """Severity first, then due date, then id; no due date sorts last."""
    return (RANK[row["severity"]],
            row["due"] is None,
            row["due"] or date.max,
            row["id"])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a short, per-owner remediation brief with top "
                    "items, evidence, fix versions, due dates and a verify command.",
        epilog="Exit codes: 0 nothing overdue, 1 an item is overdue, "
               "2 usage or input error.")
    parser.add_argument("findings", help="findings JSON export, or - for stdin")
    parser.add_argument("--owner", required=True, help="owner name to brief")
    parser.add_argument("--top", type=int, default=5,
                        help="how many top items to list (default 5)")
    parser.add_argument("--today", default=None,
                        help="as-of date, YYYY-MM-DD (default today)")
    args = parser.parse_args(argv)

    if args.top < 1:
        print("ERR --top must be at least 1", file=sys.stderr)
        return 2
    if args.today is None:
        today = date.today()
    else:
        try:
            today = date.fromisoformat(args.today)
        except ValueError:
            print("ERR --today is not a YYYY-MM-DD date: %r" % args.today,
                  file=sys.stderr)
            return 2

    try:
        rows = read_findings(load_json(args.findings, "findings file"))
    except BriefError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    owner = args.owner.strip().lower()
    mine = sorted((row for row in rows if row["owner"].lower() == owner),
                  key=sort_key)
    if not mine:
        print("OK no open findings for owner %s" % args.owner.strip())
        return 0

    counts = {name: 0 for name in ORDER}
    for row in mine:
        counts[row["severity"]] += 1
    summary = ", ".join("%d %s" % (counts[name], name)
                        for name in ORDER if counts[name])

    overdue = []
    due_soon = 0
    for row in mine:
        if row["due"] is None:
            continue
        days = (today - row["due"]).days
        if days > 0:
            overdue.append((row, days))
        elif -days <= DUE_SOON_DAYS:
            due_soon += 1

    print("BRIEF %s, as of %s" % (args.owner.strip(), today.isoformat()))
    print("%s: %s" % ("1 open finding" if len(mine) == 1
                      else "%d open findings" % len(mine), summary))
    if overdue:
        print("OVERDUE %d: %s" % (len(overdue), ", ".join(
            "%s %dd" % (row["id"], days) for row, days in overdue)))

    for place, row in enumerate(mine[:args.top], 1):
        score = "" if row["cvss"] is None else " cvss %.1f" % row["cvss"]
        print("TOP %d %s %s %s%s fix %s due %s"
              % (place, row["id"], row["asset"], row["severity"], score,
                 row["fix"] or "none",
                 row["due"].isoformat() if row["due"] else "none"))
        line = row["title"] or "no title"
        if row["evidence"]:
            line += "; " + row["evidence"]
        print("      " + line)

    print("VERIFY python3 rescan_diff.py before.json after.json")
    if overdue:
        print("FAIL %d overdue, %d due this week" % (len(overdue), due_soon))
        return 1
    print("OK %d findings, none overdue, %d due this week"
          % (len(mine), due_soon))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
