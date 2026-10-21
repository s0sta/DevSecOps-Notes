---
id: p495
title: "A route table check in Python"
slug: a-route-table-check-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [AWS, Python, VPC, Networking, Automation]
source: "LinkedIn post P495 · Network series"
linkedin_date: 2029-11-25
design: code
script: route_check.py
---

# A route table check in Python

A route table is a list of promises, and most of them are never read until something times out.

## Quick reference

The full script is at the end of this note: `route_check.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 route_check.py route_table.json
```

**Example output**

```text
ALERT no default route
ALERT blackhole 10.0.5.0/24
```

## Explained

### What it does

The script loads a route table JSON with the VPC CIDR and routes that carry destination, target and state. It checks three things: whether a default route exists, whether any route is in a blackhole state, and whether a non-local route falls inside the VPC CIDR. Each finding prints an ALERT line; any finding exits 1.

### Why these three

No default route means no general internet egress, even when the NAT gateway is healthy. A blackhole means the target was deleted and the route stayed behind. An inside route is the quiet one: a non-local path for part of the VPC's own range can shadow the local route, which is rarely what anyone meant.

### How to use it

Run `python3 route_check.py route_table.json`, or pipe the JSON in with -. Pass `--allow-no-default` for a table that should stay isolated. In CI, run it before terraform apply and let the exit code stop the merge. It reads only; it never changes a route.

> **The honest caveat:** this checks one table in isolation. It cannot see whether a subnet is associated with that table, or whether the other side of a peering has the return route.

> **The lesson:** a route is only real when the target exists and the other side agrees.

## In one line

> **A route table is a list of promises.** A promise with a deleted target is a blackhole.

**Run it in ci**

```bash
python3 route_check.py table.json
```

## Script: route_check.py

Download: [scripts/route_check.py](../scripts/route_check.py)

```python
#!/usr/bin/env python3
"""Check an AWS route table export for the failures that break egress.

Usage:
    python3 route_check.py route_table.json
    python3 route_check.py - --vpc-cidr 10.0.0.0/16
    python3 route_check.py table.json --allow-no-default

The input is JSON, either an object:
    {"vpc_cidr": "10.0.0.0/16",
     "routes": [{"destination": "0.0.0.0/0",
                 "target": "igw-0123456789abcdef0",
                 "state": "active"}]}
or a bare list of routes, in which case pass --vpc-cidr.

Checks:
    * a missing default route (0.0.0.0/0), unless --allow-no-default
    * any route whose state is not active (a blackhole)
    * a non-local route whose destination falls inside the VPC CIDR

Exit codes: 0 clean, 1 findings, 2 usage or input error.
The script is read-only: it never calls AWS and never writes a file.

Cron (daily at 06:00):
    0 6 * * * /usr/bin/python3 /opt/s0sta/route_check.py /etc/s0sta/rtb.json

CI:
    python3 route_check.py route_table.json

By s0sta.com
"""
import argparse
import ipaddress
import json
import sys


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(2)


def load(path):
    try:
        if path == "-":
            data = json.load(sys.stdin)
        else:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
    except OSError as exc:
        fail("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        fail("invalid JSON: %s" % exc)

    if isinstance(data, dict):
        routes = data.get("routes")
        vpc_cidr = data.get("vpc_cidr")
    elif isinstance(data, list):
        routes, vpc_cidr = data, None
    else:
        fail("expected a JSON object with 'routes' or a list of routes")

    if not isinstance(routes, list):
        fail("expected 'routes' to be a list")
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            fail("route %d is not an object" % index)
        for key in ("destination", "target", "state"):
            if key not in route:
                fail("route %d has no %s" % (index, key))
    return routes, vpc_cidr


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check an AWS route table JSON for missing routes, "
                    "blackholes and VPC CIDR overlaps.")
    parser.add_argument("path", nargs="?", default="-",
                        help="route table JSON file, or - for stdin (default: -)")
    parser.add_argument("--vpc-cidr",
                        help="VPC CIDR when the JSON does not carry vpc_cidr")
    parser.add_argument("--allow-no-default", action="store_true",
                        help="do not report a missing 0.0.0.0/0 route")
    args = parser.parse_args(argv)

    routes, embedded_cidr = load(args.path)
    cidr = args.vpc_cidr or embedded_cidr
    if not cidr:
        fail("no VPC CIDR: add vpc_cidr to the JSON or pass --vpc-cidr")
    try:
        vpc = ipaddress.ip_network(str(cidr), strict=False)
    except ValueError as exc:
        fail("invalid VPC CIDR %r: %s" % (cidr, exc))

    findings = []
    if not args.allow_no_default and not any(
            str(route["destination"]).strip() == "0.0.0.0/0" for route in routes):
        findings.append("no default route")

    for route in routes:
        destination = str(route["destination"]).strip()
        target = str(route["target"]).strip()
        state = str(route["state"]).strip().lower()
        if state != "active":
            if state == "blackhole":
                findings.append("blackhole " + destination)
            else:
                findings.append("not active (%s) %s" % (state or "no state", destination))
            continue
        if target == "local":
            continue
        try:
            network = ipaddress.ip_network(destination, strict=False)
        except ValueError as exc:
            fail("invalid destination %r: %s" % (destination, exc))
        if network.version != vpc.version:
            continue
        if network.subnet_of(vpc):
            findings.append("overlaps VPC " + destination)

    if findings:
        for finding in findings:
            print("ALERT " + finding)
        return 1
    print("OK route table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
