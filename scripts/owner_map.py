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
