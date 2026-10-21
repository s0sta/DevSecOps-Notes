---
id: p753
title: "The exception that never expires"
slug: the-exception-that-never-expires
sections: [devsecops]
topic: "Python scripts"
tags: [RiskManagement, GRC, CyberSecurity, Python, VulnerabilityManagement]
source: "LinkedIn post P753 · ASM series"
linkedin_date: 2031-07-20
design: code
script: exception_register.py
---

# The exception that never expires

The exception was approved for thirty days in March. It is still open in October, the owner has left, and the reason field says temporary.

## Quick reference

The full script is at the end of this note: `exception_register.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 exception_register.py register.json --today 2026-10-21
```

**Example output**

```text
EXPIRED 2: EXC-101 50d past, EXC-102 no expiry
FAIL 2 expired, 1 missing owner
```

## Explained

### What it does

`exception_register.py` reads a register JSON: finding, owner, reason and expires. Expired means the date passed, or there is no date at all, because an exception with no end date is a permanent acceptance. It reports the ones expiring inside `--soon` days, thirty by default, and the ones with no owner. An expired row exits 1.

### What the screen shows

The fourteen lines fix the as-of date, walk every row and collect the expired list. On the dirty register it ends with EXPIRED 2: EXC-101 50d past, EXC-102 no expiry and FAIL 2 expired, 1 missing owner, then exits 1.

### How to run it

`python3 exception_register.py register.json --today 2026-10-21`. Run it on a Monday cron and send the expired list to the risk owner, not the ticket queue.

### The fix

Close the exception with a patch, or renew it with a new date, a reason and an owner. Delete the rows nobody can defend.

### Prevention

Make the expiry mandatory at approval, cap it at ninety days, and require the risk owner to re-approve. A register that renews itself is a list of things you decided not to fix.

> **The honest caveat:** a register only knows what somebody wrote down; an exception agreed in chat is invisible, and treating no date as expired is a policy choice.

> **The lesson:** an exception is a promise to revisit.

## In one line

> **Every exception needs an end date.** An approval with no expiry is a permanent exception.

**Audit the register**

```bash
python3 exception_register.py reg.json
```

## Script: exception_register.py

Download: [scripts/exception_register.py](../scripts/exception_register.py)

```python
#!/usr/bin/env python3
"""Find the exceptions that expired, the ones about to, and the ones with no owner.

Reads a risk-exception register as JSON:

    {"exceptions": [
        {"id": "EXC-101", "finding": "CVE-2024-3094", "owner": "platform",
         "reason": "vendor patch due in Q2", "expires": "2026-09-30"},
        ...]}

Three rules decide the report:

  * expires before --today, or no expires value at all  -> expired
  * expires within --soon days                         -> expiring soon
  * owner empty or missing                             -> missing owner

A missing expiry is treated as expired. An exception with no end date is a
permanent acceptance, which is the failure this script exists to catch. A
register row that expires today is expiring soon, not expired: the owner still
has the day.

An exception can appear under two headings, for example expired and missing
owner. The counts are per category, not a partition, and the last line repeats
the two that matter.

Usage:
    python3 exception_register.py register.json
    python3 exception_register.py register.json --today 2026-10-21
    python3 exception_register.py register.json --soon 14
    cat register.json | python3 exception_register.py -

Exit codes: 0 nothing expired, 1 at least one expired, 2 usage or invalid
input.

CI (block the release when an exception has run out):
    python3 exception_register.py risk-register.json --today "$(date +%F)"

Cron (Mondays, mail the expired and soon lists to the risk owner):
    0 6 * * 1 python3 /opt/s0sta/exception_register.py /exports/register.json --soon 30

The script is read-only: one JSON file or stdin, no API calls, no writes.
--today exists so a report can be reproduced; a live run uses the real date.
The register is only as good as its entries: an approved exception that was
never written down is invisible here.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys
from datetime import date

DEFAULT_SOON_DAYS = 30


class RegisterError(Exception):
    """Anything that should end the run with exit code 2."""


def load_json(source, label):
    """Read JSON from a path, or stdin when source is '-'."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise RegisterError("cannot read %s: %s" % (label, exc))
    except ValueError as exc:
        raise RegisterError("%s is not valid JSON: %s" % (label, exc))


def parse_day(value, label):
    """Parse a YYYY-MM-DD date, raising RegisterError on anything else."""
    if not isinstance(value, str):
        raise RegisterError("%s must be a YYYY-MM-DD string" % label)
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise RegisterError("%s is not a YYYY-MM-DD date: %r" % (label, value))


def read_register(doc):
    """Validate the register and return one row per exception."""
    if isinstance(doc, dict):
        doc = doc.get("exceptions")
    if not isinstance(doc, list):
        raise RegisterError(
            "the register must be a list or an object with exceptions")
    rows = []
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise RegisterError("exception %d is not an object" % number)
        eid = item.get("id") or "row %d" % number
        if not isinstance(eid, str):
            raise RegisterError("exception %d id must be a string" % number)
        eid = eid.strip()
        finding = item.get("finding")
        if not isinstance(finding, str) or not finding.strip():
            raise RegisterError("%s needs a finding" % eid)
        owner = item.get("owner")
        if owner is None:
            owner = ""
        elif not isinstance(owner, str):
            raise RegisterError("%s owner must be a string" % eid)
        expires = item.get("expires")
        if expires is None or expires == "":
            day = None
        else:
            day = parse_day(expires, "%s expires" % eid)
        rows.append({"id": eid, "finding": finding.strip(),
                     "owner": owner.strip(), "expires": day})
    return rows


def classify(rows, today, soon_days):
    """Return expired, expiring-soon and missing-owner lists."""
    expired, upcoming, no_owner = [], [], []
    for row in rows:
        if row["expires"] is None:
            expired.append((row, None))
        else:
            left = (row["expires"] - today).days
            if left < 0:
                expired.append((row, -left))
            elif left <= soon_days:
                upcoming.append((row, left))
        if not row["owner"]:
            no_owner.append(row)
    upcoming.sort(key=lambda pair: (pair[1], pair[0]["id"]))
    expired.sort(key=lambda pair: pair[0]["id"])
    return expired, upcoming, no_owner


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report expired, expiring and unowned risk exceptions "
                    "from a register JSON file.",
        epilog="Exit codes: 0 nothing expired, 1 at least one expired, "
               "2 usage or input error.")
    parser.add_argument("register", help="exception register JSON, or - for stdin")
    parser.add_argument("--today", default=None,
                        help="as-of date, YYYY-MM-DD (default today)")
    parser.add_argument("--soon", type=int, default=DEFAULT_SOON_DAYS,
                        help="days that count as expiring soon (default 30)")
    args = parser.parse_args(argv)

    if args.soon < 0:
        print("ERR --soon cannot be negative", file=sys.stderr)
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
        rows = read_register(load_json(args.register, "register file"))
    except RegisterError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not rows:
        print("OK 0 exceptions in register")
        return 0

    expired, upcoming, no_owner = classify(rows, today, args.soon)
    print("REGISTER %d exceptions, as of %s"
          % (len(rows), today.isoformat()))

    if upcoming:
        parts = []
        for row, left in upcoming:
            parts.append("%s %dd" % (row["id"], left))
        print("SOON %d: %s" % (len(upcoming), ", ".join(parts)))

    if no_owner:
        print("NO OWNER %d: %s"
              % (len(no_owner), ", ".join(row["id"] for row in no_owner)))

    if expired:
        parts = []
        for row, days in expired:
            if days is None:
                parts.append("%s no expiry" % row["id"])
            else:
                parts.append("%s %dd past" % (row["id"], days))
        print("EXPIRED %d: %s" % (len(expired), ", ".join(parts)))
        print("FAIL %d expired, %d missing owner"
              % (len(expired), len(no_owner)))
        return 1

    if no_owner:
        print("WARN 0 expired, %d missing owner" % len(no_owner))
        return 0

    active = len(rows) - len(upcoming)
    print("OK %d active, %d due within %d days"
          % (active, len(upcoming), args.soon))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
