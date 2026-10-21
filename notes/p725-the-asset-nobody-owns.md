---
id: p725
title: "The asset nobody owns"
slug: the-asset-nobody-owns
sections: [devsecops]
topic: "Python scripts"
tags: [Python, CyberSecurity, ITAM, AttackSurface, DevOps]
source: "LinkedIn post P725 · ASM series"
linkedin_date: 2031-05-15
design: code
script: owner_map.py
---

# The asset nobody owns

The scanner finds a host called blog.acme.com. Three people in the room recognise it. None of them will say they own it, and the CMDB row has a blank owner.

## Quick reference

The full script is at the end of this note: `owner_map.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 owner_map.py assets.csv cmdb.csv
```

**Example output**

```text
OWNER 5 assets, 1 unowned, 1 in conflict
CONFLICT api.acme.com tag bob, cmdb erin
```

## Explained

### What it does

`owner_map.py` joins an asset inventory to a CMDB export on the asset name. The inventory carries tags, and owner:alice is the one that matters. An asset is unowned when there is no row or the owner is blank. It is in conflict when the CMDB lists two owners, or when the tag and the CMDB disagree.

### What the screen shows

The fourteen lines read both CSVs, build the owner and tag maps, compare them and print OWNER 5 assets, 1 unowned, 1 in conflict and CONFLICT api.acme.com tag bob, cmdb erin.

### How to run it

`python3 owner_map.py assets.csv cmdb.csv`. Exit 0 is one agreed owner per asset, 1 is a finding, 2 is bad input. Run it weekly, and before any access review.

### The fix

For blog.acme.com, pick a person and a cost centre, then write both in the CMDB. For api.acme.com, decide whether bob or erin owns it: the tag came from the builder, the CMDB from the payer.

### Prevention

Make owner a required field at asset creation, and generate the tag from the CMDB instead of asking teams to type it twice.

> **The honest caveat:** the owner field is not accountability. It only means something when the person agrees to patch, pay for or delete the asset.

> **The lesson:** discovery finds the asset, and ownership is a human decision.

## In one line

> **Discovery finds it. Someone must own it.** An asset with no owner has no patch window and no budget.

**Ask who owns it**

```bash
python3 owner_map.py assets.csv cmdb.csv
```

## Script: owner_map.py

Download: [scripts/owner_map.py](../scripts/owner_map.py)

```python
#!/usr/bin/env python3
"""owner_map.py - join an asset inventory to a CMDB and find the assets nobody owns.

Discovery tells you a host exists. It does not tell you who patches it, who
pays for it, or who agrees to the risk. That answer lives in the CMDB, and the
join between the two is where asset management usually fails: a host with no
row, a row with a blank owner, a tag that names one person while the CMDB
names another.

This script reads two CSV exports and joins them on the asset column.

Assets (what discovery found), with a tags column of semicolon-separated
key:value pairs; owner:alice is the one that matters here:

    asset,tags
    www.example.com,owner:alice;env:prod;cc:CC-104
    blog.example.com,env:prod

CMDB (what the organisation thinks it owns):

    asset,owner,team,cost_centre
    www.example.com,alice,web,CC-104
    api.example.com,erin,api,CC-207

Findings are:

    unowned    an asset with no CMDB row, or a row whose owner is blank or
               one of the placeholders -, unknown, none, tbd or n/a
    conflict   two different non-empty owners in the CMDB, or a tag owner
               that disagrees with the single CMDB owner

The cost centre is printed with each conflict so the finding has a budget
attached. Entries that exist only in the CMDB are out of scope here; that is
the stale side of the comparison, and shadow_it.py reports it.

Usage:
    python3 owner_map.py assets.csv cmdb.csv
    python3 owner_map.py assets.csv cmdb.csv --max-list 10
    python3 owner_map.py --help

Cron or CI (weekly, fail the job when an asset has no owner):
    0 7 * * 1 python3 /opt/s0sta/owner_map.py /var/lib/s0sta/assets.csv /var/lib/s0sta/cmdb.csv

Exit codes: 0 every asset has one agreed owner, 1 at least one unowned asset
or conflict, 2 usage error, unreadable input or missing columns.

Read-only: opens the two CSVs and prints. It writes nothing, changes nothing
and makes no network call.

By s0sta.com
"""
import argparse
import csv
import sys

DEFAULT_MAX_LIST = 50
PLACEHOLDERS = {"", "-", "unknown", "none", "tbd", "n/a", "na", "null"}


class InputError(Exception):
    """An input that cannot be read as an inventory or CMDB export."""


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


def tag_owners(tags):
    """Return the owner values in a semicolon-separated tag string."""
    owners = []
    for tag in tags.split(";"):
        tag = tag.strip()
        if not tag:
            continue
        key, _, value = tag.partition(":")
        if key.strip().lower() == "owner" and value.strip():
            owners.append(value.strip())
    return owners


def real_owner(value):
    """Return the owner, or an empty string for a placeholder."""
    value = (value or "").strip()
    return "" if value.lower() in PLACEHOLDERS else value


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Join an asset inventory to a CMDB and report unowned "
                    "assets and ownership conflicts.")
    parser.add_argument("assets", help="inventory CSV with asset and tags columns")
    parser.add_argument("cmdb", help="CMDB CSV with asset, owner, team, cost_centre")
    parser.add_argument("--max-list", type=int, default=DEFAULT_MAX_LIST,
                        metavar="N", help="print at most N lines per finding "
                                          "(default 50)")
    args = parser.parse_args(argv)
    if args.max_list < 1:
        print("owner_map: --max-list must be at least 1", file=sys.stderr)
        return 2

    try:
        asset_rows = read_csv(args.assets, ("asset", "tags"))
        cmdb_rows = read_csv(args.cmdb, ("asset", "owner"))
    except InputError as exc:
        print("owner_map: %s" % exc, file=sys.stderr)
        return 2

    inventory = []
    tags_by_asset = {}
    for row in asset_rows:
        asset = row["asset"].strip().lower()
        if not asset:
            continue
        if asset not in tags_by_asset:
            inventory.append(asset)
            tags_by_asset[asset] = row.get("tags", "")
        else:
            tags_by_asset[asset] += ";" + row.get("tags", "")

    cmdb = {}
    for row in cmdb_rows:
        asset = row["asset"].strip().lower()
        owner = real_owner(row.get("owner"))
        cost = row.get("cost_centre", "") or "-"
        cmdb.setdefault(asset, []).append((owner, cost))

    unowned = []
    conflicts = []
    for asset in inventory:
        rows = cmdb.get(asset, [])
        owners = {owner for owner, _cost in rows if owner}
        cost = rows[0][1] if rows else "-"
        shares = tag_owners(tags_by_asset.get(asset, ""))
        tag = shares[0] if shares else ""

        if not rows:
            unowned.append((asset, "not in CMDB"))
            continue
        if not owners:
            unowned.append((asset, "no owner in CMDB"))
            continue
        if len(owners) > 1:
            conflicts.append((asset, "cmdb " + ", ".join(sorted(owners)), cost))
            continue
        only = sorted(owners)[0]
        if len(set(shares)) > 1:
            conflicts.append((asset, "tag " + ", ".join(sorted(set(shares))),
                              cost))
        elif tag and tag.lower() != only.lower():
            conflicts.append((asset, "tag %s, cmdb %s" % (tag, only), cost))

    print("OWNER %d assets, %d unowned, %d in conflict"
          % (len(inventory), len(unowned), len(conflicts)))

    for asset, why in unowned[:args.max_list]:
        print("UNOWNED %s (%s)" % (asset, why))
    for asset, why, cost in conflicts[:args.max_list]:
        print("CONFLICT %s %s (%s)" % (asset, why, cost))

    return 1 if (unowned or conflicts) else 0


if __name__ == "__main__":
    sys.exit(main())
```
