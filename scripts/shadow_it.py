#!/usr/bin/env python3
"""shadow_it.py - compare discovered assets with the CMDB in both directions.

A scanner finds what answers. A CMDB records what the organisation believes it
owns. The gap between them has two sides, and both are findings:

    unknown    an asset that answers but has no CMDB entry; first_seen is the
               day discovery first saw it, so the age is the exposure clock
    stale      a CMDB entry that no longer answers; added is the day it was
               registered, so the age is how long the record has been wrong

This script reads two CSV exports and reports both sides with an age in days.

Discovered:

    asset,first_seen
    www.example.com,2026-01-04
    api-lab.example.com,2026-10-14

CMDB:

    asset,owner,added
    www.example.com,alice,2025-06-01
    old.example.com,frank,2024-03-02

Dates are ISO dates or ISO timestamps; only the first ten characters are
used. --today pins the clock so a report is reproducible. A future date is
clamped to zero days rather than printed as a negative age.

Usage:
    python3 shadow_it.py discovered.csv cmdb.csv
    python3 shadow_it.py discovered.csv cmdb.csv --today 2026-10-21
    python3 shadow_it.py discovered.csv cmdb.csv --max-list 10
    python3 shadow_it.py --help

Cron or CI (daily, fail the job on either side of the gap):
    45 6 * * * python3 /opt/s0sta/shadow_it.py /var/lib/s0sta/discovered.csv /var/lib/s0sta/cmdb.csv --today "$(date +%F)"

Exit codes: 0 the two lists agree, 1 at least one unknown or stale asset,
2 usage error, unreadable input, missing columns or a bad date.

Read-only: opens the two CSVs and prints. It writes nothing, changes nothing
and makes no network call. Pairs with owner_map.py: this finds the gap, that
one finds who should close it.

By s0sta.com
"""
import argparse
import csv
import sys
from datetime import date

DEFAULT_MAX_LIST = 50


class InputError(Exception):
    """An input that cannot be read as an asset export."""


def read_csv(path, required):
    """Return rows as lowercase-key dicts, or raise InputError."""
    try:
        handle = sys.stdin if path == "-" else open(path, "r", encoding="utf-8",
                                                    newline="")
    except OSError as exc:
        raise InputError("%s: %s" % (path, exc.strerror or exc))
    try:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise InputError("%s: no header row" % path)
        fields = [name.strip().lower() for name in reader.fieldnames]
        for column in required:
            if column not in fields:
                raise InputError("%s: header needs a %s column" % (path, column))
        rows = []
        for raw in reader:
            row = {}
            for key, value in raw.items():
                if key is None:
                    continue
                row[key.strip().lower()] = (value or "").strip()
            if row.get("asset"):
                rows.append(row)
    finally:
        if handle is not sys.stdin:
            handle.close()
    if not rows:
        raise InputError("%s: no usable rows" % path)
    return rows


def parse_day(value, where):
    """Return a date from an ISO date or timestamp, or raise InputError."""
    text = (value or "").strip()
    if not text:
        raise InputError("%s: missing date" % where)
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        raise InputError("%s: bad date %r" % (where, value))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare discovered assets with the CMDB and report "
                    "unknown assets and stale entries with their age.")
    parser.add_argument("discovered", help="CSV with asset and first_seen columns")
    parser.add_argument("cmdb", help="CSV with asset, owner and added columns")
    parser.add_argument("--today", metavar="YYYY-MM-DD",
                        help="pin the report date (default: today, UTC)")
    parser.add_argument("--max-list", type=int, default=DEFAULT_MAX_LIST,
                        metavar="N", help="print at most N lines per side "
                                          "(default 50)")
    args = parser.parse_args(argv)
    if args.max_list < 1:
        print("shadow_it: --max-list must be at least 1", file=sys.stderr)
        return 2

    try:
        discovered_rows = read_csv(args.discovered, ("asset", "first_seen"))
        cmdb_rows = read_csv(args.cmdb, ("asset", "added"))
        today = parse_day(args.today, "--today") if args.today else date.today()

        discovered = {}
        for row in discovered_rows:
            asset = row["asset"].strip().lower()
            seen = parse_day(row.get("first_seen"), "%s first_seen" % asset)
            if asset not in discovered or seen < discovered[asset]:
                discovered[asset] = seen

        cmdb = {}
        for row in cmdb_rows:
            asset = row["asset"].strip().lower()
            added = parse_day(row.get("added"), "%s added" % asset)
            if asset not in cmdb or added < cmdb[asset]:
                cmdb[asset] = added
    except InputError as exc:
        print("shadow_it: %s" % exc, file=sys.stderr)
        return 2

    unknown = []
    for asset in sorted(discovered):
        if asset in cmdb:
            continue
        age = (today - discovered[asset]).days
        unknown.append((asset, discovered[asset].isoformat(), max(0, age)))

    stale = []
    for asset in sorted(cmdb):
        if asset in discovered:
            continue
        age = (today - cmdb[asset]).days
        stale.append((asset, cmdb[asset].isoformat(), max(0, age)))
    stale.sort(key=lambda item: (-item[2], item[0]))

    print("SHADOW %d discovered, %d unknown, %d stale"
          % (len(discovered), len(unknown), len(stale)))

    for asset, seen, age in unknown[:args.max_list]:
        print("UNKNOWN %s first seen %s (%dd)" % (asset, seen, age))
    for asset, added, age in stale[:args.max_list]:
        print("STALE %s in CMDB since %s (%dd)" % (asset, added, age))

    return 1 if (unknown or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
