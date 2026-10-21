#!/usr/bin/env python3
"""s3_cost_hotspots.py - rank S3 buckets by monthly cost and flag cold STANDARD data.

Reads an S3 inventory JSON and a price table JSON, estimates one month of
cost per bucket, ranks the buckets and flags STANDARD buckets whose access
density is cold enough to move to a cheaper storage class.

Inventory shape (a bare list of buckets also works):

    {"buckets": [
      {"name": "media", "class": "STANDARD",
       "bytes": 43980465111040, "requests": 2000},
      {"name": "archive", "class": "GLACIER",
       "bytes": 2199023255552, "requests": 1000}
    ]}

Price table shape, dollars per GiB-month and per 1,000 requests:

    {"STANDARD": {"gb": 0.023, "req": 0.005},
     "STANDARD_IA": {"gb": 0.0125, "req": 0.01},
     "GLACIER": {"gb": 0.0036, "req": 0.03}}

Requests are one number, not split by GET and PUT, so the table's req price
is an assumption you choose and the estimate is only as good as it. The
cold rule is deliberately simple: a STANDARD bucket is flagged when it holds
at least --cold-gb and receives fewer than --cold-requests requests per GiB
per month. The saving is the storage difference only; retrieval and request
charges on the move are not modelled.

Usage:
    python3 s3_cost_hotspots.py inventory.json --prices prices.json
    python3 s3_cost_hotspots.py inventory.json --prices prices.json --budget 500
    python3 s3_cost_hotspots.py --help

CI (fail the job when the month is over budget):
    python3 s3_cost_hotspots.py /etc/s0sta/s3.json --prices /etc/s0sta/prices.json --budget 2000 || exit 1

Cron (weekly cost report to the FinOps channel):
    0 7 * * 1 python3 /opt/s0sta/s3_cost_hotspots.py /etc/s0sta/s3.json --prices /etc/s0sta/prices.json

Exit codes: 0 under budget with no cold bucket, 1 over budget or at least
one cold bucket, 2 usage, unreadable JSON, an unknown storage class or a
record that does not match the shape.

Read-only: both files are opened for reading only. No object is copied,
moved or deleted and no AWS API is called; the lifecycle command printed at
the end is a suggestion for a human.

By s0sta.com
"""
import argparse
import json
import sys

GIB = 1024.0 ** 3


def load_json(path):
    """Read a JSON file, or raise ValueError."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("%s: %s" % (path, exc))


def number(value, where, field):
    """Return a non-negative whole number, or raise ValueError."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s: %s must be a number" % (where, field))
    if value < 0 or int(value) != value:
        raise ValueError("%s: %s must be a non-negative whole number"
                         % (where, field))
    return int(value)


def load_prices(path):
    """Return {class: {'gb': float, 'req': float}}, or raise ValueError."""
    document = load_json(path)
    if not isinstance(document, dict) or not document:
        raise ValueError("%s: expected an object of storage classes" % path)
    prices = {}
    for name, entry in document.items():
        where = "%s: class %s" % (path, name)
        if not isinstance(entry, dict):
            raise ValueError("%s is not an object" % where)
        for key in ("gb", "req"):
            value = entry.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("%s: %s must be a number" % (where, key))
            if value < 0:
                raise ValueError("%s: %s must be zero or more" % (where, key))
        prices[name] = {"gb": float(entry["gb"]), "req": float(entry["req"])}
    return prices


def load_buckets(path, prices):
    """Return the validated bucket list, or raise ValueError."""
    document = load_json(path)
    if isinstance(document, dict):
        buckets = document.get("buckets")
    else:
        buckets = document
    if not isinstance(buckets, list):
        raise ValueError("%s: expected a list or an object with a buckets list"
                         % path)
    if not buckets:
        raise ValueError("%s: no buckets" % path)
    seen = set()
    rows = []
    for index, bucket in enumerate(buckets):
        where = "%s bucket %d" % (path, index + 1)
        if not isinstance(bucket, dict):
            raise ValueError("%s is not an object" % where)
        name = bucket.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("%s: name is missing" % where)
        name = name.strip()
        if name in seen:
            raise ValueError("%s: duplicate bucket %s" % (where, name))
        seen.add(name)
        storage = bucket.get("class")
        if not isinstance(storage, str) or storage not in prices:
            raise ValueError("%s: unknown class %r" % (where, storage))
        size = number(bucket.get("bytes"), where, "bytes")
        requests = number(bucket.get("requests"), where, "requests")
        rows.append({"name": name, "class": storage,
                     "bytes": size, "requests": requests})
    return rows


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Rank S3 buckets by monthly cost and flag cold data.")
    parser.add_argument("inventory", help="S3 inventory JSON")
    parser.add_argument("--prices", required=True,
                        help="price table JSON, dollars per GiB-month")
    parser.add_argument("--budget", type=float, default=1000.0,
                        help="monthly budget in dollars (default 1000)")
    parser.add_argument("--top", type=int, default=10,
                        help="buckets to rank (default 10)")
    parser.add_argument("--cold-gb", type=float, default=100.0,
                        help="minimum size for a cold flag (default 100)")
    parser.add_argument("--cold-requests", type=float, default=1.0,
                        help="requests per GiB per month below this is cold "
                             "(default 1.0)")
    args = parser.parse_args(argv)
    if args.budget < 0:
        parser.error("--budget must be zero or more")
    if args.top < 1:
        parser.error("--top must be at least 1")
    if args.cold_gb < 0 or args.cold_requests < 0:
        parser.error("--cold-gb and --cold-requests must be zero or more")
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        prices = load_prices(args.prices)
        buckets = load_buckets(args.inventory, prices)
    except ValueError as exc:
        print("s3_cost_hotspots: %s" % exc, file=sys.stderr)
        return 2

    rows = []
    for bucket in buckets:
        price = prices[bucket["class"]]
        gib = bucket["bytes"] / GIB
        cost = gib * price["gb"] + bucket["requests"] / 1000.0 * price["req"]
        rows.append((cost, bucket, gib))
    rows.sort(key=lambda row: (-row[0], row[1]["name"]))
    total = sum(row[0] for row in rows)

    for rank, (cost, bucket, gib) in enumerate(rows[:args.top], 1):
        print("COST %d %s $%.2f/mo %s %.1f GiB"
              % (rank, bucket["name"], cost, bucket["class"], gib))
    if len(rows) > args.top:
        print("SHOWN %d of %d buckets" % (args.top, len(rows)))
    print("TOTAL $%.2f/mo budget $%.2f" % (total, args.budget))

    cold = []
    others = [name for name in prices if name != "STANDARD"]
    cheap = min(others, key=lambda name: prices[name]["gb"]) if others else None
    for _cost, bucket, gib in rows:
        if bucket["class"] != "STANDARD" or gib < args.cold_gb:
            continue
        density = bucket["requests"] / gib if gib else 0.0
        if density >= args.cold_requests:
            continue
        cold.append(bucket["name"])
        line = ("COLD %s %.2f req/GiB in STANDARD"
                % (bucket["name"], density))
        if cheap and prices[cheap]["gb"] < prices["STANDARD"]["gb"]:
            saving = (prices["STANDARD"]["gb"] - prices[cheap]["gb"]) * gib
            line += " -> %s saves $%.2f/mo" % (cheap, saving)
        print(line)

    problems = []
    if total > args.budget:
        problems.append("over budget by $%.2f" % (total - args.budget))
    if cold:
        problems.append("%d cold bucket%s" % (len(cold),
                                              "" if len(cold) == 1 else "s"))
    if problems:
        print("FLAG " + ", ".join(problems))
        if cold and cheap:
            print("SUGGEST aws s3api put-bucket-lifecycle-configuration "
                  "--bucket %s --lifecycle-configuration file://lifecycle.json"
                  % cold[0])
        return 1
    print("OK no cold data, under budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
