#!/usr/bin/env python3
"""Turn overdue findings into escalation tiers, with a reason for each move.

Reads a findings export and an owner-to-manager map:

    findings.json
    {"findings": [
        {"id": "E-3001", "owner": "platform", "severity": "critical",
         "due": "2026-10-22"},
        ...]}

    owners.json
    {"platform": "Omar Hani", "infra": "Sara Ali", "app": "Omar Hani"}

The tiers are rules, not opinions:

    reminder    due in 0 to --remind-days days (default 7)
    manager     overdue 1 to --manager-days days (default 14)
    committee   overdue more than --manager-days days, or critical and
                overdue at least --critical-days days (default 3)

Every tier prints its rule and its counts, and every owner in the manager or
committee tier prints with the manager who receives it. The last line repeats
the two counts that matter. A finding with no due date cannot be escalated and
is listed as NO DUE; an owner with no entry in the map is listed as NO MANAGER,
because an escalation with nowhere to go is not an escalation.

Usage:
    python3 escalation.py findings.json owners.json
    python3 escalation.py findings.json owners.json --today 2026-10-21
    python3 escalation.py findings.json owners.json --remind-days 3
    cat findings.json | python3 escalation.py - owners.json

Exit codes: 0 nothing past the reminder tier, 1 at least one manager or
committee item, 2 usage or invalid input.

CI (weekly, fail the job when anything reaches the committee):
    python3 escalation.py findings.json owners.json --today "$(date +%F)"

Cron (daily at 07:30, after the owners have had a week to act):
    30 7 * * * python3 /opt/s0sta/escalation.py /exports/findings.json /opt/s0sta/owners.json

The script is read-only: two JSON files or stdin, no API calls, no writes.
The thresholds are policy choices; change them to match your SLA, then keep
them fixed for a quarter so the trend means something. The script counts
findings, not risk: a critical reminder can matter more than a low committee
item, and the tier line says which rule put it there.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys
from datetime import date

RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class EscalationError(Exception):
    """Anything that should end the run with exit code 2."""


def load_json(source, label):
    """Read JSON from a path, or stdin when source is '-'."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise EscalationError("cannot read %s: %s" % (label, exc))
    except ValueError as exc:
        raise EscalationError("%s is not valid JSON: %s" % (label, exc))


def parse_day(value, label):
    """Parse a YYYY-MM-DD date, returning None when it is absent."""
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise EscalationError("%s must be a YYYY-MM-DD string" % label)
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise EscalationError("%s is not a YYYY-MM-DD date: %r" % (label, value))


def read_findings(doc):
    """Validate the export and return one row per finding."""
    if isinstance(doc, dict):
        doc = doc.get("findings")
    if not isinstance(doc, list):
        raise EscalationError(
            "the export must be a list or an object with findings")
    rows = []
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise EscalationError("finding %d is not an object" % number)
        fid = item.get("id") or "finding %d" % number
        if not isinstance(fid, str):
            raise EscalationError("finding %d id must be a string" % number)
        owner = item.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            raise EscalationError("%s needs an owner" % fid.strip())
        severity = item.get("severity")
        if not isinstance(severity, str) or severity.strip().lower() not in RANK:
            raise EscalationError("%s has unknown severity %r"
                                  % (fid.strip(), severity))
        rows.append({
            "id": fid.strip(),
            "owner": owner.strip(),
            "severity": severity.strip().lower(),
            "due": parse_day(item.get("due"), "%s due" % fid.strip()),
        })
    return rows


def read_owners(doc):
    """Validate the owner-to-manager map."""
    if not isinstance(doc, dict):
        raise EscalationError("the owners file must be a JSON object")
    mapping = {}
    for owner, manager in doc.items():
        if not isinstance(owner, str) or not owner.strip():
            raise EscalationError("the owners file has an empty owner name")
        if not isinstance(manager, str) or not manager.strip():
            raise EscalationError("owner %r needs a manager name" % owner)
        mapping[owner.strip().lower()] = manager.strip()
    return mapping


def count(number, one, many):
    """Return '1 finding' or '2 findings'."""
    return "%d %s" % (number, one if number == 1 else many)


def tier_line(name, rows, rule):
    """Print one tier summary line."""
    owners = len({row["owner"] for row in rows})
    print("%s %s, %s, %s"
          % (name, count(len(rows), "finding", "findings"),
             count(owners, "owner", "owners"), rule))


def oldest_days(rows, today):
    """Return the age of the oldest item in a group."""
    return max((today - row["due"]).days for row in rows)


def owner_lines(name, rows, managers, today):
    """Print one line per owner in a tier, with the manager and the oldest age."""
    grouped = {}
    for row in rows:
        grouped.setdefault(row["owner"], []).append(row)
    ordered = sorted(grouped, key=lambda owner: (-oldest_days(grouped[owner], today),
                                                 owner))
    parts = []
    for owner in ordered:
        items = grouped[owner]
        manager = managers.get(owner.lower(), "no manager")
        parts.append("%s (%s) %s, oldest %s"
                     % (owner, manager,
                        count(len(items), "item", "items"),
                        count(oldest_days(items, today), "day", "days")))
    print("%s: %s" % (name.lower(), "; ".join(parts)))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sort overdue findings into reminder, manager and "
                    "committee tiers with the rule that moved each one.",
        epilog="Exit codes: 0 nothing past the reminder tier, 1 manager or "
               "committee items, 2 usage or input error.")
    parser.add_argument("findings", help="findings JSON export, or - for stdin")
    parser.add_argument("owners", help="owner-to-manager map, JSON object")
    parser.add_argument("--today", default=None,
                        help="as-of date, YYYY-MM-DD (default today)")
    parser.add_argument("--remind-days", type=int, default=7,
                        help="days before the due date that count as a reminder "
                             "(default 7)")
    parser.add_argument("--manager-days", type=int, default=14,
                        help="days overdue before the committee tier (default 14)")
    parser.add_argument("--critical-days", type=int, default=3,
                        help="days a critical finding may be overdue before the "
                             "committee tier (default 3)")
    args = parser.parse_args(argv)

    for name, value in (("--remind-days", args.remind_days),
                        ("--manager-days", args.manager_days),
                        ("--critical-days", args.critical_days)):
        if value < 0:
            print("ERR %s cannot be negative" % name, file=sys.stderr)
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
        managers = read_owners(load_json(args.owners, "owners file"))
    except EscalationError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    reminder, manager, committee, no_due = [], [], [], []
    for row in rows:
        if row["due"] is None:
            no_due.append(row["id"])
            continue
        left = (row["due"] - today).days
        if left >= 0 and left <= args.remind_days:
            reminder.append(row)
        elif left < 0:
            overdue = -left
            if (overdue > args.manager_days
                    or (row["severity"] == "critical"
                        and overdue >= args.critical_days)):
                committee.append(row)
            else:
                manager.append(row)

    print("FINDINGS %d, as of %s" % (len(rows), today.isoformat()))
    if reminder:
        tier_line("REMINDER", reminder,
                  "due in 0-%d days" % args.remind_days)
    if manager:
        tier_line("MANAGER", manager,
                  "overdue 1-%d days" % args.manager_days)
        owner_lines("MANAGER", manager, managers, today)
    if committee:
        tier_line("COMMITTEE", committee,
                  "overdue %d+ days or critical %d+ days"
                  % (args.manager_days + 1, args.critical_days))
        owner_lines("COMMITTEE", committee, managers, today)
    if no_due:
        print("NO DUE %d: %s" % (len(no_due), ", ".join(no_due)))
    missing = sorted({row["owner"] for row in manager + committee
                      if row["owner"].lower() not in managers})
    if missing:
        print("NO MANAGER %d: %s" % (len(missing), ", ".join(missing)))

    if committee or manager:
        print("FAIL %d committee, %d manager"
              % (len(committee), len(manager)))
        return 1
    print("OK %s, nothing escalated"
          % count(len(reminder), "reminder", "reminders"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
