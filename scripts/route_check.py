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
