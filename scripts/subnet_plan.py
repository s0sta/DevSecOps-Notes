#!/usr/bin/env python3
"""subnet_plan.py - plan an IPv4 range and catch overlapping subnets.

Splits a base CIDR into a target prefix (a /24 by default), prints one row
per subnet with its network, first and last host, broadcast and usable
count, then checks every --check CIDR against the plan with
ipaddress.overlaps(). IPv4 only. Read-only: it opens no sockets and writes
no files.

Exit codes: 0 clean, 1 overlap found, 2 usage or input error.

Usage:
    python3 subnet_plan.py 10.0.0.0/16
    python3 subnet_plan.py 10.0.0.0/16 --prefix 20
    python3 subnet_plan.py 10.0.0.0/20 --check 10.0.8.0/23
    python3 subnet_plan.py 10.0.0.0/20 --check 10.0.8.0/23 -q
    python3 subnet_plan.py 10.0.0.0/16 --prefix 24 --json

Cron or CI, fail the job when a planned range collides:
    python3 subnet_plan.py 10.0.0.0/16 --check 10.0.8.0/23 -q || exit 1

By s0sta.com
"""
import argparse
import ipaddress
import json
import sys

# A /12 split into /24s is 4,096 rows; refuse anything larger than that.
MAX_SUBNETS = 4096


class PlanError(Exception):
    """Anything that should end the run with exit code 2."""


def network_of(text, label):
    """Parse an IPv4 network, clearing host bits, or raise PlanError."""
    try:
        net = ipaddress.ip_network(text, strict=False)
    except ValueError as exc:
        raise PlanError("%s is not a CIDR: %s" % (label, exc))
    if net.version != 4:
        raise PlanError("%s is IPv6; this planner is IPv4 only" % label)
    return net


def usable(net):
    """Host addresses: /31 is a point-to-point pair (RFC 3021), /32 is one."""
    if net.prefixlen >= 31:
        return net.num_addresses
    return net.num_addresses - 2


def bounds(net):
    """Return (first host, last host, broadcast) as strings."""
    if net.prefixlen >= 31:
        first = net.network_address
        last = net.network_address + net.num_addresses - 1
        return str(first), str(last), "n/a"
    return (str(net.network_address + 1),
            str(net.broadcast_address - 1),
            str(net.broadcast_address))


def build_nets(base, prefix):
    """List the target subnets, refusing a split that would flood the output."""
    count = 2 ** (prefix - base.prefixlen)
    if count > MAX_SUBNETS:
        raise PlanError("that split makes %s subnets; the limit is %s"
                        % (format(count, ","), format(MAX_SUBNETS, ",")))
    return list(base.subnets(new_prefix=prefix))


def find_overlaps(nets, checks):
    """Every (planned subnet, checked range) pair that overlaps."""
    return [(net, check) for net in nets for check in checks if net.overlaps(check)]


def print_table(base, prefix, nets):
    """The human-readable plan."""
    print("PLAN %s as /%d: %d subnets, %d addresses"
          % (base, prefix, len(nets), base.num_addresses))
    print("%-5s %-18s %-15s %-15s %-15s %6s"
          % ("#", "network", "first", "last", "broadcast", "usable"))
    for i, net in enumerate(nets, 1):
        first, last, bcast = bounds(net)
        print("%-5d %-18s %-15s %-15s %-15s %6d"
              % (i, str(net), first, last, bcast, usable(net)))


def emit(args, base, nets, checks, overlaps):
    """Print the table or the JSON summary, then the findings."""
    if args.json:
        report = {
            "base": str(base),
            "prefix": args.prefix,
            "count": len(nets),
            "addresses": base.num_addresses,
            "checks": [str(check) for check in checks],
            "overlaps": [{"network": str(net), "check": str(check)}
                         for net, check in overlaps],
            "ok": not overlaps,
        }
        print(json.dumps(report, indent=None if args.quiet else 2, sort_keys=True))
        return

    if not args.quiet:
        print_table(base, args.prefix, nets)
    for net, check in overlaps:
        print("OVERLAP %s %s" % (net, check))
    if overlaps:
        hit = len({str(net) for net, _ in overlaps})
        print("ALERT %d of %d subnets overlap %d checked range(s)"
              % (hit, len(nets), len(checks)))
    else:
        extra = "" if not checks else " with %d checked range(s)" % len(checks)
        print("OK %d subnets, no overlap%s" % (len(nets), extra))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Plan an IPv4 subnet split and flag ranges that overlap it.",
        epilog="Exit codes: 0 clean, 1 overlap, 2 usage or input error.")
    parser.add_argument("base", help="base CIDR, for example 10.0.0.0/16")
    parser.add_argument("--prefix", type=int, default=24, metavar="N",
                        help="target prefix length, default 24 (max 4096 rows)")
    parser.add_argument("--check", action="append", default=[], metavar="CIDR",
                        help="range to test against the plan, repeatable")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print findings and the summary only")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON summary instead of the table")
    args = parser.parse_args(argv)

    try:
        base = network_of(args.base, "base")
        if not 0 <= args.prefix <= 32:
            raise PlanError("--prefix must be between 0 and 32")
        if args.prefix < base.prefixlen:
            raise PlanError("--prefix /%d is shorter than the base /%d"
                            % (args.prefix, base.prefixlen))
        checks = [network_of(text, "--check") for text in args.check]
        nets = build_nets(base, args.prefix)
        overlaps = find_overlaps(nets, checks)
    except PlanError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    emit(args, base, nets, checks, overlaps)
    return 1 if overlaps else 0


if __name__ == "__main__":
    sys.exit(main())
