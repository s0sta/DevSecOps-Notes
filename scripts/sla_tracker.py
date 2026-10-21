#!/usr/bin/env python3
"""Track vulnerability fix SLAs from a CSV.

Usage:
    python3 sla_tracker.py findings.csv
    python3 sla_tracker.py findings.csv --now 2026-10-21
    python3 sla_tracker.py findings.csv --now 2026-10-21 --json
    python3 sla_tracker.py --help

The CSV has four columns:

    id,severity,found_at,fixed_at
    VULN-1042,critical,2026-10-12,2026-10-21
    VULN-1077,high,2026-09-26,

severity is critical, high or medium. The windows are 7, 30 and 90 days.
found_at and fixed_at are ISO dates or datetimes; fixed_at stays empty while
a finding is open. A finding is breached when its age is past the window, and
at risk when it is open and has used 80 percent of the window (day 5.6 for
critical, 24 for high, 72 for medium).

Exit codes: 0 inside SLA, 1 breach or at-risk finding, 2 usage or input error.
Read-only: the CSV is opened for reading and never modified.

Cron: 0 7 * * * python3 /opt/s0sta/sla_tracker.py /var/tmp/findings.csv
CI:   python3 sla_tracker.py findings.csv --now "$(date -u +%F)"

By s0sta.com
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone

SLA_DAYS = {"critical": 7, "high": 30, "medium": 90}
COLUMNS = ("id", "severity", "found_at", "fixed_at")
DAY = 86400.0


class InputError(Exception):
    """A CSV row or header that cannot be used."""


def parse_when(value, label):
    """Parse an ISO date or datetime into an aware UTC datetime."""
    text = (value or "").strip()
    if not text:
        return None
    try:
        if len(text) == 10:
            when = datetime.strptime(text, "%Y-%m-%d")
        else:
            when = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise InputError("bad %s: %r (expected ISO date or datetime)"
                         % (label, value))
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


def load_rows(path):
    """Read the CSV and return a list of dicts."""
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            missing = [name for name in COLUMNS if name not in fields]
            if missing:
                raise InputError("%s is missing column(s): %s"
                                 % (path, ", ".join(missing)))
            return list(reader)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except csv.Error as exc:
        raise InputError("%s is not valid CSV: %s" % (path, exc))


def assess(row, now, ratio):
    """Return a dict describing one finding's SLA state."""
    row_id = (row.get("id") or "").strip() or "?"
    severity = (row.get("severity") or "").strip().lower()
    if severity not in SLA_DAYS:
        raise InputError("row %s: unknown severity %r" % (row_id, severity))

    try:
        found = parse_when(row.get("found_at"), "found_at")
        fixed = parse_when(row.get("fixed_at"), "fixed_at")
    except InputError as exc:
        raise InputError("row %s: %s" % (row_id, exc))
    if found is None:
        raise InputError("row %s: found_at is required" % row_id)

    limit = SLA_DAYS[severity]
    end = fixed or now
    age = (end - found).total_seconds() / DAY
    if age < 0:
        raise InputError("row %s: fixed_at is before found_at" % row_id)

    if age > limit:
        state = "breach"
    elif fixed is None and age >= ratio * limit:
        state = "at-risk"
    else:
        state = "inside"

    return {
        "id": row_id,
        "severity": severity,
        "found_at": found.strftime("%Y-%m-%d"),
        "fixed_at": fixed.strftime("%Y-%m-%d") if fixed else "",
        "open": fixed is None,
        "age_days": round(age, 1),
        "sla_days": limit,
        "state": state,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="sla_tracker.py",
        description="Report breached and at-risk vulnerability SLAs from a CSV.")
    parser.add_argument("csv", help="CSV with id,severity,found_at,fixed_at")
    parser.add_argument("--now", default=None,
                        help="evaluate at this ISO date or datetime "
                             "(default: now, UTC)")
    parser.add_argument("--at-risk-ratio", type=float, default=0.8,
                        help="fraction of the window used before at-risk "
                             "(default: 0.8)")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON object instead of text lines")
    args = parser.parse_args(argv)

    if not 0 < args.at_risk_ratio <= 1:
        parser.error("--at-risk-ratio must be greater than 0 and at most 1")

    try:
        now = parse_when(args.now, "--now") if args.now else \
            datetime.now(timezone.utc)
        # parse_when returns None only for an empty string.
        if now is None:
            parser.error("--now cannot be empty")
        rows = load_rows(args.csv)
        results = [assess(row, now, args.at_risk_ratio) for row in rows]
    except InputError as exc:
        parser.error(str(exc))

    breaches = [r for r in results if r["state"] == "breach"]
    at_risk = [r for r in results if r["state"] == "at-risk"]
    inside = len(results) - len(breaches) - len(at_risk)

    if args.json:
        print(json.dumps({
            "now": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rows": len(results),
            "breaches": breaches,
            "at_risk": at_risk,
            "inside_sla": inside,
            "clean": not breaches and not at_risk,
        }, indent=2, sort_keys=True))
    else:
        for item in breaches:
            print("BREACH %s %s %.1fd of %dd" % (
                item["id"], item["severity"],
                item["age_days"], item["sla_days"]))
        for item in at_risk:
            print("AT RISK %s %s %.1fd of %dd" % (
                item["id"], item["severity"],
                item["age_days"], item["sla_days"]))
        print("SLA: %d breached, %d at risk, %d inside, %d %s"
              % (len(breaches), len(at_risk), inside, len(results),
                 "row" if len(results) == 1 else "rows"))

    return 1 if breaches or at_risk else 0


if __name__ == "__main__":
    sys.exit(main())
