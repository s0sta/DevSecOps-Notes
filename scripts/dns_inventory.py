#!/usr/bin/env python3
"""dns_inventory.py - read a dig export and find the records that point at nothing.

A DNS zone accumulates records faster than it loses them. A trial ends, an
appliance is returned, a SaaS account is closed, and the CNAME or the A record
stays behind, still answering or still pointing at a name that no longer
exists. This script reads a plain export of the records and reports three
kinds of finding:

    dangling   a CNAME whose chain ends at a name with status NXDOMAIN
    missing    a name with no A or AAAA record and no CNAME to resolve through
    outside    a CNAME, MX or NS target that leaves the given scope

The input is a CSV export with a header row. Required columns are name and
type; value and status are read when present. The export looks like:

    name,type,value,status
    www.example.com,A,10.0.0.5,NOERROR
    blog.example.com,CNAME,old.example.io,NOERROR
    old.example.io,A,,NXDOMAIN
    example.com,MX,10 mail.example.com,NOERROR

Status is any resolver verdict, usually NOERROR or NXDOMAIN. An empty status
means the export did not record one; it is never read as NXDOMAIN.

Usage:
    python3 dns_inventory.py dns.csv --scope example.com
    python3 dns_inventory.py dns.csv --scope example.com --scope example.net
    python3 dns_inventory.py dns.csv --scope example.com --max-list 10
    python3 dns_inventory.py --help

Cron or CI (daily, fail the job when a record points at nothing):
    15 5 * * * python3 /opt/s0sta/dns_inventory.py /var/lib/s0sta/dns.csv --scope example.com

Exit codes: 0 no finding, 1 at least one finding, 2 usage error, unreadable
input, missing columns or no usable rows.

Read-only: opens the given CSV and prints. It writes nothing, changes nothing
and makes no DNS query; the export is the input.

By s0sta.com
"""
import argparse
import csv
import sys

DEFAULT_MAX_LIST = 50
NAMESERVER_TYPES = ("CNAME", "MX", "NS")
ADDRESS_TYPES = ("A", "AAAA")


class InputError(Exception):
    """An input that cannot be read as a DNS export."""


def read_rows(path):
    """Return the CSV rows as dicts with lowercase keys, or raise InputError."""
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
        if "name" not in fields or "type" not in fields:
            raise InputError("%s: header needs name and type columns" % path)
        rows = []
        for raw in reader:
            row = {}
            for key, value in raw.items():
                if key is None:
                    continue
                row[key.strip().lower()] = (value or "").strip()
            if not row.get("name"):
                continue
            rows.append(row)
    finally:
        if handle is not sys.stdin:
            handle.close()
    if not rows:
        raise InputError("%s: no usable rows" % path)
    return rows


def normalise_host(value):
    """Return a lowercase hostname without the trailing dot."""
    return value.strip().lower().rstrip(".")


def target_host(record_type, value):
    """Return the hostname a record points at, or None for address records."""
    value = value.strip()
    if not value:
        return None
    if record_type == "MX":
        parts = value.split()
        value = parts[-1]
    if record_type in NAMESERVER_TYPES:
        return normalise_host(value)
    return None


def in_scope(host, scopes):
    """True when host equals a scope domain or sits under one."""
    for scope in scopes:
        if host == scope or host.endswith("." + scope):
            return True
    return False


def resolve_chain(start, cname_map):
    """Follow CNAMEs from start. Return (final_name, path, looped)."""
    path = []
    current = start
    seen = {start}
    for _ in range(12):
        nxt = cname_map.get(current)
        if not nxt:
            return current, path, False
        if nxt in seen:
            return nxt, path, True
        path.append(nxt)
        seen.add(nxt)
        current = nxt
    return current, path, True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Find dangling CNAMEs, names without addresses and "
                    "out-of-scope targets in a dig export.")
    parser.add_argument("records", help="CSV export of DNS records, or - for stdin")
    parser.add_argument("--scope", action="append", required=True,
                        metavar="DOMAIN", help="in-scope domain; repeat as needed")
    parser.add_argument("--max-list", type=int, default=DEFAULT_MAX_LIST,
                        metavar="N", help="print at most N lines per finding "
                                          "(default 50)")
    args = parser.parse_args(argv)
    if args.max_list < 1:
        print("dns_inventory: --max-list must be at least 1", file=sys.stderr)
        return 2

    try:
        scopes = []
        for value in args.scope:
            scope = normalise_host(value)
            if not scope or "*" in scope or "/" in scope or " " in scope:
                raise InputError("bad --scope value: %r" % value)
            scopes.append(scope)
        rows = read_rows(args.records)
    except InputError as exc:
        print("dns_inventory: %s" % exc, file=sys.stderr)
        return 2

    names = []
    cname_map = {}
    nxdomain = set()
    for row in rows:
        name = normalise_host(row["name"])
        record_type = row.get("type", "").upper()
        value = row.get("value", "")
        status = row.get("status", "").upper()
        if record_type not in ("A", "AAAA", "CNAME", "MX", "NS", "TXT", "SRV"):
            continue
        names.append((name, record_type, value, status))
        if record_type == "CNAME" and value:
            cname_map.setdefault(name, normalise_host(value))
        if status == "NXDOMAIN":
            nxdomain.add(name)

    if not names:
        print("dns_inventory: no usable records in %s" % args.records,
              file=sys.stderr)
        return 2

    unique_names = {row[0] for row in names}
    owners = {row[0] for row in names}

    dangling = []
    seen_dangling = set()
    for name, record_type, value, _status in names:
        if record_type != "CNAME" or not value:
            continue
        target = normalise_host(value)
        final, path, looped = resolve_chain(target, cname_map)
        if final in nxdomain:
            route = " -> ".join([target] + path)
            key = (name, target)
            if key not in seen_dangling:
                seen_dangling.add(key)
                dangling.append((name, route, looped))

    cname_owners = set(cname_map)
    missing = []
    addressed = set()
    for name, record_type, value, status in names:
        if record_type in ADDRESS_TYPES and value and status != "NXDOMAIN":
            addressed.add(name)
    for name in sorted(unique_names):
        if name in nxdomain or name in cname_owners or name in addressed:
            continue
        if name in owners:
            missing.append(name)

    outside = []
    seen_outside = set()
    for name, record_type, value, status in names:
        if record_type not in NAMESERVER_TYPES or status == "NXDOMAIN":
            continue
        host = target_host(record_type, value)
        if not host or host in nxdomain:
            continue
        if not in_scope(host, scopes):
            key = (name, record_type, host)
            if key not in seen_outside:
                seen_outside.add(key)
                outside.append((name, record_type, host))

    print("DNS %d records, %d names, %d dangling, %d without A/AAAA, "
          "%d outside scope"
          % (len(names), len(unique_names), len(dangling), len(missing),
             len(outside)))

    for name, route, looped in dangling[:args.max_list]:
        suffix = " (loop)" if looped else " (NXDOMAIN)"
        print("DANGLING %s -> %s%s" % (name, route, suffix))
    for name in missing[:args.max_list]:
        print("MISSING %s has no A or AAAA record" % name)
    for name, record_type, host in outside[:args.max_list]:
        print("OUTSIDE %s -> %s %s" % (name, record_type, host))

    return 1 if (dangling or missing or outside) else 0


if __name__ == "__main__":
    sys.exit(main())
