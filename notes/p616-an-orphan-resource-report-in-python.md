---
id: p616
title: "An orphan resource report in Python"
slug: an-orphan-resource-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [AWS, FinOps, CloudCost, Python, CloudNative]
source: "LinkedIn post P616 · PythonFixes series"
linkedin_date: 2030-09-03
design: code
script: orphan_resources.py
---

# An orphan resource report in Python

A cost review finds a line for EBS that no team recognises. The volume is unattached, the address is idle, and the snapshot is older than the service it came from.

## Quick reference

The full script is at the end of this note: `orphan_resources.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 orphan_resources.py cloud.json
```

**Example output**

```text
ORPHAN {'volume': 1, 'snapshot': 1, 'address': 1} WASTE $21.65/mo
```

## Explained

### What it does

The script reads an inventory of volumes, addresses and snapshots, or one flat list with a kind field. It flags a volume in state available, an address with no association and a snapshot older than `--snapshot-days`, then prices each one with an overrideable rate.

### What the screen shows

The 14 lines classify each row, check the snapshot age against a 90-day cut-off and add the cost: ORPHAN {'volume': 1, 'snapshot': 1, 'address': 1} WASTE $21.65/mo. The full script adds the resource id, size, reason and a line per orphan.

### How to run it

`python3 orphan_resources.py cloud.json`, weekly, from the inventory export. `--snapshot-days 90` is the default; set the prices to your contract if it is not list.

### The fix

Tag the resource, find the owner, and decide: keep it with a note, or snapshot and delete it. The tags command is the first step, not the delete.

### Prevention

Require an owner tag at create time and report orphans weekly. A tag is cheaper than an investigation.

> **The honest caveat:** an unattached volume can be a disaster-recovery copy that must stay, and a snapshot can be the only copy of a deleted database. The report names candidates; a person decides.

> **The lesson:** the invoice is per account, so the orphan has no owner.

## In one line

> **An idle disk still bills.** The invoice is per account, so nobody sees the orphan.

**Check one orphan**

```bash
aws ec2 describe-volumes --volume-ids vol-0a1
```

## Script: orphan_resources.py

Download: [scripts/orphan_resources.py](../scripts/orphan_resources.py)

```python
#!/usr/bin/env python3
"""orphan_resources.py - report idle cloud resources and their monthly waste.

Reads a cloud inventory JSON and flags the resources that bill every month
without serving anything: volumes in state available, elastic IPs with no
association, and snapshots older than --snapshot-days. Each orphan gets an
estimated monthly cost and the total is printed at the end. Nothing is
deleted or changed.

Inventory shape, either three lists:

    {"volumes": [
       {"id": "vol-0a1", "size_gb": 100, "state": "available"}
     ],
     "addresses": [
       {"id": "eipalloc-1", "public_ip": "203.0.113.7",
        "state": "unassociated"}
     ],
     "snapshots": [
       {"id": "snap-9", "size_gb": 200,
        "created": "2025-01-01T00:00:00Z"}
     ]}

or one flat list with a kind field (volume, address, snapshot). A volume is
an orphan only in state available; in-use and attaching volumes are left
alone. An address is an orphan when it has no association_id and its state
is not associated. created accepts a date or an ISO timestamp.

Prices are us-east-1 list prices at the time of writing: gp3 EBS at $0.08
per GiB-month, EBS snapshots at $0.05 per GiB-month, and a public IPv4
address at $3.65 per month. Every price can be overridden, because list
prices change and this is an estimate, not an invoice.

Usage:
    python3 orphan_resources.py inventory.json
    python3 orphan_resources.py inventory.json --snapshot-days 180
    python3 orphan_resources.py inventory.json --volume-price 0.10
    python3 orphan_resources.py --help

CI (fail the job when an orphan appears):
    python3 orphan_resources.py /etc/s0sta/cloud.json || exit 1

Cron (weekly waste report):
    0 7 * * 1 python3 /opt/s0sta/orphan_resources.py /etc/s0sta/cloud.json

Exit codes: 0 no orphan, 1 at least one orphan, 2 usage, unreadable JSON or
a record that does not match the shape.

Read-only: reads one JSON file. It does not call a cloud API, change a tag
or delete a resource; the describe-tags command printed at the end is a
suggestion for a human.

By s0sta.com
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

KINDS = ("volume", "address", "snapshot")
LISTS = (("volume", "volumes"), ("address", "addresses"),
         ("snapshot", "snapshots"))


def load_json(path):
    """Read a JSON file, or raise ValueError."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("%s: %s" % (path, exc))


def whole(value, where, field):
    """Return a non-negative whole number, or raise ValueError."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s: %s must be a number" % (where, field))
    if value < 0 or int(value) != value:
        raise ValueError("%s: %s must be a non-negative whole number"
                         % (where, field))
    return int(value)


def parse_time(text, where, field="created"):
    """Parse an ISO 8601 timestamp; a naive value is treated as UTC."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("%s: %s is missing" % (where, field))
    raw = text.strip()
    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"
    try:
        value = datetime.fromisoformat(raw)
    except ValueError:
        raise ValueError("%s: bad %s %r" % (where, field, text))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def inventory_rows(document, path):
    """Return a flat list of rows with a kind field, or raise ValueError."""
    if isinstance(document, dict) and "resources" in document:
        items = document["resources"]
        if not isinstance(items, list):
            raise ValueError("%s: resources must be a list" % path)
        rows = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError("%s resource %d is not an object"
                                 % (path, index + 1))
            rows.append(dict(item))
        return rows
    if isinstance(document, dict):
        rows = []
        known = False
        for kind, key in LISTS:
            if key not in document:
                continue
            known = True
            items = document[key]
            if not isinstance(items, list):
                raise ValueError("%s: %s must be a list" % (path, key))
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    raise ValueError("%s %s %d is not an object"
                                     % (path, key, index + 1))
                row = dict(item)
                row["kind"] = kind
                rows.append(row)
        if not known:
            raise ValueError("%s: expected resources or volumes, addresses "
                             "and snapshots" % path)
        return rows
    raise ValueError("%s: expected a JSON object" % path)


def validate(rows):
    """Check every row and return the normalised records, or raise ValueError."""
    seen = set()
    records = []
    for index, row in enumerate(rows):
        where = "resource %d" % (index + 1)
        kind = row.get("kind")
        if kind not in KINDS:
            raise ValueError("%s: kind must be volume, address or snapshot"
                             % where)
        rid = row.get("id")
        if not isinstance(rid, str) or not rid.strip():
            raise ValueError("%s: id is missing" % where)
        rid = rid.strip()
        if (kind, rid) in seen:
            raise ValueError("%s: duplicate %s %s" % (where, kind, rid))
        seen.add((kind, rid))
        record = {"kind": kind, "id": rid}
        if kind == "volume":
            record["size_gb"] = whole(row.get("size_gb"), where, "size_gb")
            state = row.get("state")
            if not isinstance(state, str) or not state.strip():
                raise ValueError("%s: state is missing" % where)
            record["state"] = state.strip()
        elif kind == "address":
            state = row.get("state")
            if state is not None and not isinstance(state, str):
                raise ValueError("%s: state must be a string" % where)
            assoc = row.get("association_id")
            if assoc is not None and not isinstance(assoc, str):
                raise ValueError("%s: association_id must be a string" % where)
            record["state"] = (state or "").strip() or "unassociated"
            record["association_id"] = assoc or ""
            public = row.get("public_ip")
            record["public_ip"] = public.strip() if isinstance(public, str) else ""
        else:
            record["size_gb"] = whole(row.get("size_gb"), where, "size_gb")
            record["created"] = parse_time(row.get("created"), where)
        records.append(record)
    return records


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Report orphaned cloud resources and monthly waste.")
    parser.add_argument("inventory", help="cloud inventory JSON")
    parser.add_argument("--snapshot-days", type=int, default=90,
                        help="flag snapshots older than this (default 90)")
    parser.add_argument("--volume-price", type=float, default=0.08,
                        help="EBS price per GiB-month (default 0.08)")
    parser.add_argument("--snapshot-price", type=float, default=0.05,
                        help="snapshot price per GiB-month (default 0.05)")
    parser.add_argument("--address-price", type=float, default=3.65,
                        help="idle public IPv4 price per month (default 3.65)")
    parser.add_argument("--now",
                        help="ISO 8601 reference time for snapshot ages")
    args = parser.parse_args(argv)
    if args.snapshot_days < 0:
        parser.error("--snapshot-days must be zero or more")
    for name in ("volume_price", "snapshot_price", "address_price"):
        if getattr(args, name) < 0:
            parser.error("--%s must be zero or more" % name.replace("_", "-"))
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        document = load_json(args.inventory)
        rows = inventory_rows(document, args.inventory)
        records = validate(rows)
        as_of = parse_time(args.now, "--now", "timestamp") if args.now else \
            datetime.now(timezone.utc)
    except ValueError as exc:
        print("orphan_resources: %s" % exc, file=sys.stderr)
        return 2

    cutoff = as_of - timedelta(days=args.snapshot_days)
    orphans = []
    for record in records:
        kind = record["kind"]
        if kind == "volume":
            if record["state"] == "available":
                cost = record["size_gb"] * args.volume_price
                orphans.append((cost, record, "available"))
        elif kind == "address":
            if not record["association_id"] and record["state"] != "associated":
                orphans.append((args.address_price, record, "unassociated"))
        else:
            if record["created"] < cutoff:
                age = max(0, (as_of - record["created"]).days)
                cost = record["size_gb"] * args.snapshot_price
                orphans.append((cost, record, "%dd" % age))

    orphans.sort(key=lambda row: (-row[0], row[1]["kind"], row[1]["id"]))
    for cost, record, reason in orphans:
        if record["kind"] == "address":
            detail = record["public_ip"] or "-"
            print("ORPHAN address %s %s %s $%.2f/mo"
                  % (record["id"], detail, reason, cost))
        elif record["kind"] == "snapshot":
            print("ORPHAN snapshot %s %d GiB %s $%.2f/mo"
                  % (record["id"], record["size_gb"], reason, cost))
        else:
            print("ORPHAN volume %s %d GiB %s $%.2f/mo"
                  % (record["id"], record["size_gb"], reason, cost))
    if not orphans:
        print("OK no orphaned volumes, addresses or snapshots")
        return 0

    waste = sum(cost for cost, _record, _reason in orphans)
    print("WASTE %d resources $%.2f/mo" % (len(orphans), waste))
    print("SUGGEST aws ec2 describe-tags --filters "
          "Name=resource-id,Values=%s" % orphans[0][1]["id"])
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
