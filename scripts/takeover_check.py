#!/usr/bin/env python3
"""takeover_check.py - match CNAME targets against known takeover fingerprints.

A subdomain takeover needs three things: a DNS record that points at a
third-party service, a name at that service that nobody has claimed, and a
provider that lets the next person claim it. This script checks the first two
from an export, and the third from a saved HTTP body when you have one.

The DNS input is a CSV export with a header row. Either a two-column export:

    name,target
    blog.example.com,acme.github.io

or a dig-style export with name, type, value and status, where CNAME rows are
used and the other rows are ignored.

The fingerprint file is JSON, a list of objects or an object with a
"fingerprints" list. Each entry is:

    {"service": "GitHub Pages",
     "cname": "github.io",
     "marker": "There isn't a GitHub Pages site here."}

cname is the suffix a target must end with (a leading *. is ignored). marker
is the text the provider serves on an unclaimed name. A suffix match alone is
a candidate, not a takeover; the marker is the evidence.

--snapshot takes a JSON object mapping hostname to the HTTP body you saved
from that host. With a body, the marker confirms the finding. Without one, a
candidate is reported as UNVERIFIED, because it cannot be cleared from an
export alone. The script never fetches anything.

Usage:
    python3 takeover_check.py dns.csv --fingerprints fingerprints.json
    python3 takeover_check.py dns.csv --fingerprints fingerprints.json --snapshot bodies.json
    python3 takeover_check.py --help

Cron or CI (daily, fail the job on a confirmed or unverified candidate):
    30 6 * * * python3 /opt/s0sta/takeover_check.py /var/lib/s0sta/dns.csv --fingerprints /opt/s0sta/takeover.json --snapshot /var/lib/s0sta/bodies.json

Exit codes: 0 nothing matched or every match was cleared by a snapshot,
1 at least one confirmed or unverified match, 2 usage error or bad input.

Read-only: opens the given files and prints. It writes nothing, changes
nothing and makes no network call.

By s0sta.com
"""
import argparse
import csv
import json
import sys

DEFAULT_MAX_LIST = 50
# Services that serve a claim page to anyone who registers the name. The
# marker strings are the ones those services return today; verify them before
# you trust a VULN line.
BUILTIN = [
    {"service": "GitHub Pages", "cname": "github.io",
     "marker": "There isn't a GitHub Pages site here."},
    {"service": "Amazon S3", "cname": "s3.amazonaws.com",
     "marker": "NoSuchBucket"},
    {"service": "Heroku", "cname": "herokuapp.com",
     "marker": "No such app"},
    {"service": "Azure", "cname": "azurewebsites.net",
     "marker": "404 Web Site not found"},
    {"service": "Fastly", "cname": "fastly.net",
     "marker": "Fastly error: unknown domain"},
]


class InputError(Exception):
    """An input that cannot be read as a CNAME or fingerprint export."""


def read_text(path):
    """Return the file as text, or raise InputError."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise InputError("%s: %s" % (path, exc.strerror or exc))


def normalise_host(value):
    """Return a lowercase hostname without the trailing dot."""
    return value.strip().lower().rstrip(".")


def normalise_suffix(value):
    """Return a fingerprint suffix without a leading wildcard or dot."""
    suffix = normalise_host(value)
    if suffix.startswith("*."):
        suffix = suffix[2:]
    return suffix.lstrip(".")


def load_cnames(path):
    """Return (name, target) pairs from a CSV export, or raise InputError."""
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
        if "name" not in fields:
            raise InputError("%s: header needs a name column" % path)
        direct = "target" in fields or "cname" in fields
        if not direct and not ("type" in fields and "value" in fields):
            raise InputError("%s: header needs target or type and value" % path)
        pairs = []
        for raw in reader:
            row = {}
            for key, value in raw.items():
                if key is None:
                    continue
                row[key.strip().lower()] = (value or "").strip()
            name = normalise_host(row.get("name", ""))
            if not name:
                continue
            if direct:
                target = row.get("target") or row.get("cname") or ""
            else:
                if (row.get("type", "").upper() != "CNAME"):
                    continue
                target = row.get("value", "")
            target = normalise_host(target)
            if target:
                pairs.append((name, target))
    finally:
        if handle is not sys.stdin:
            handle.close()
    if not pairs:
        raise InputError("%s: no CNAME records" % path)
    return pairs


def load_fingerprints(path):
    """Return the fingerprint list, or raise InputError."""
    if not path:
        return [dict(item) for item in BUILTIN]
    text = read_text(path)
    if not text.strip():
        raise InputError("%s: empty input" % path)
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise InputError("%s is not JSON: %s" % (path, exc))
    if isinstance(data, dict) and isinstance(data.get("fingerprints"), list):
        data = data["fingerprints"]
    if not isinstance(data, list):
        raise InputError("%s: expected a JSON list of fingerprints" % path)
    items = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        service = str(entry.get("service", "")).strip()
        cname = normalise_suffix(str(entry.get("cname", "")))
        marker = str(entry.get("marker", ""))
        if not service or not cname:
            continue
        items.append({"service": service, "cname": cname, "marker": marker})
    if not items:
        raise InputError("%s: no fingerprint has service and cname" % path)
    return items


def load_snapshot(path):
    """Return a host to body map, or raise InputError."""
    if not path:
        return None
    text = read_text(path)
    if not text.strip():
        raise InputError("%s: empty input" % path)
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise InputError("%s is not JSON: %s" % (path, exc))
    if not isinstance(data, dict):
        raise InputError("%s: expected a JSON object of host to body" % path)
    bodies = {}
    for host, body in data.items():
        if isinstance(body, str):
            bodies[normalise_host(host)] = body
    if not bodies:
        raise InputError("%s: no host bodies" % path)
    return bodies


def matches(target, suffix):
    """True when target is the suffix or a name under it."""
    return target == suffix or target.endswith("." + suffix)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Match CNAME targets against takeover fingerprints and "
                    "confirm with a saved HTTP body.")
    parser.add_argument("dns", help="CSV export with name,target or dig columns")
    parser.add_argument("--fingerprints", metavar="JSON",
                        help="fingerprint JSON; without it a small built-in list is used")
    parser.add_argument("--snapshot", metavar="JSON",
                        help="JSON object mapping host to a saved HTTP body")
    parser.add_argument("--max-list", type=int, default=DEFAULT_MAX_LIST,
                        metavar="N", help="print at most N lines per state "
                                          "(default 50)")
    args = parser.parse_args(argv)
    if args.max_list < 1:
        print("takeover_check: --max-list must be at least 1", file=sys.stderr)
        return 2

    try:
        pairs = load_cnames(args.dns)
        fingerprints = load_fingerprints(args.fingerprints)
        snapshot = load_snapshot(args.snapshot)
    except InputError as exc:
        print("takeover_check: %s" % exc, file=sys.stderr)
        return 2

    confirmed = []
    unverified = []
    cleared = []
    for name, target in pairs:
        for fingerprint in fingerprints:
            if not matches(target, fingerprint["cname"]):
                continue
            body = snapshot.get(name) if snapshot is not None else None
            if body is None:
                unverified.append((name, target, fingerprint["service"]))
            elif fingerprint["marker"] and fingerprint["marker"] in body:
                confirmed.append((name, target, fingerprint["service"]))
            else:
                cleared.append((name, target, fingerprint["service"]))
            break

    matched = len(confirmed) + len(unverified) + len(cleared)
    print("TAKEOVER %d CNAMEs, %d matched, %d confirmed"
          % (len(pairs), matched, len(confirmed)))

    if not matched:
        print("OK no CNAME matches a known fingerprint")
        return 0

    for name, target, service in confirmed[:args.max_list]:
        print("VULN %s -> %s (%s)" % (name, target, service))
    for name, target, service in unverified[:args.max_list]:
        print("UNVERIFIED %s -> %s (%s, no snapshot)"
              % (name, target, service))
    for name, target, service in cleared[:args.max_list]:
        print("CLEARED %s -> %s (%s, marker absent)"
              % (name, target, service))

    return 1 if (confirmed or unverified) else 0


if __name__ == "__main__":
    sys.exit(main())
