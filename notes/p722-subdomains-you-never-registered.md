---
id: p722
title: "Subdomains you never registered"
slug: subdomains-you-never-registered
sections: [devsecops]
topic: "Python scripts"
tags: [Python, CyberSecurity, AttackSurface, Recon, DevOps]
source: "LinkedIn post P722 · ASM series"
linkedin_date: 2031-05-08
design: code
script: ct_inventory.py
---

# Subdomains you never registered

At 09:40 a staging API nobody remembers deploying answers on 443 with a valid certificate. It is not in the inventory, not the CMDB, and not the last four pentest scopes.

## Quick reference

The full script is at the end of this note: `ct_inventory.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 ct_inventory.py ct.json --scope acme.com
```

**Example output**

```text
CT 8 in scope, 3 new
NEW admin.acme.com, api.staging.acme.com, vpn.acme.com
```

## Explained

### What it does

`ct_inventory.py` reads a `crt.sh` JSON export, takes name_value and common_name from every certificate, lowercases each name and strips the trailing dot. Wildcards are dropped, because \*.acme.com is a policy, not a host. Anything outside `--scope` is dropped too. The unique hostnames that remain are diffed against a known list.

### What the screen shows

The fourteen lines normalise the export, drop wildcards and out-of-scope hosts, then diff against the known file. On the dirty fixture: CT 8 in scope, 3 new and NEW admin.acme.com, api.staging.acme.com, vpn.acme.com.

### How to run it

`python3 ct_inventory.py ct.json --scope acme.com --known known.txt`. Exit 0 is clean, 1 is a new host, 2 is bad input. Run it weekly, or in CI before a scope is signed.

### The fix

api.staging is a live staging API, admin a panel on a marketing subdomain, vpn a decommissioned appliance whose A record still answers. Add the first two to the CMDB with an owner, and remove the third at the DNS provider.

### Prevention

Diff on every certificate issuance, not once a year. A host becomes findable the day its certificate is issued.

> **The honest caveat:** CT logs certificates, not services. A host with a certificate can be dead, and a host without one can still be alive.

> **The lesson:** the certificate log is the inventory you did not write.

## In one line

> **Your next asset is already public.** The log is append-only, and it was never yours to edit.

**Diff the log**

```bash
python3 ct_inventory.py ct.json
```

## Script: ct_inventory.py

Download: [scripts/ct_inventory.py](../scripts/ct_inventory.py)

```python
#!/usr/bin/env python3
"""ct_inventory.py - turn a certificate transparency export into a host diff.

Every certificate a public CA issues is published to the certificate
transparency logs, and crt.sh will hand you the result as JSON. The log is
append-only and public, so a hostname becomes discoverable the day its
certificate is issued, whether or not anyone remembered to put it in the
inventory.

This script reads a crt.sh JSON export (or the same shape from another
aggregator), takes name_value and common_name from every certificate,
normalises each name to a lowercase hostname, drops wildcards, drops anything
outside the given scope, and reports the hosts that are not in the known list.

The input is a JSON list of certificate objects, each with a name_value field:

    [{"name_value": "www.example.com\\n*.example.com"},
     {"name_value": "api.example.com", "common_name": "api.example.com"}]

The known list is one hostname per line, lowercased on read. Comments start
with #. Without --known, every in-scope host counts as new, which is the
useful first run: it prints the surface you never wrote down.

Usage:
    python3 ct_inventory.py crt.json --scope example.com --known known.txt
    python3 ct_inventory.py crt.json --scope example.com --scope example.net
    python3 ct_inventory.py crt.json --scope example.com --known known.txt --max-list 20
    python3 ct_inventory.py --help

Cron or CI (weekly, fail the job when a new host appears):
    0 6 * * 1 python3 /opt/s0sta/ct_inventory.py /var/lib/s0sta/crt.json --scope example.com --known /opt/s0sta/known.txt

Exit codes: 0 no new hosts, 1 at least one new host, 2 usage error,
unreadable or malformed input, or no in-scope names at all.

Read-only: opens the given files or stdin, parses JSON and prints. It writes
nothing, changes nothing and makes no network call. Fetch the export first,
then run this against it.

By s0sta.com
"""
import argparse
import json
import sys

DEFAULT_MAX_LIST = 50


class InputError(Exception):
    """An input that cannot be used as certificate or scope data."""


def read_text(path):
    """Return the file or stdin as text, or raise InputError."""
    try:
        if path == "-":
            return sys.stdin.read()
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise InputError("%s: %s" % (path, exc.strerror or exc))


def load_certs(path):
    """Return the list of certificate objects, or raise InputError."""
    text = read_text(path)
    if not text.strip():
        raise InputError("%s: empty input" % path)
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise InputError("%s is not JSON: %s" % (path, exc))
    if isinstance(data, dict):
        for key in ("certificates", "results", "data"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            raise InputError("%s: no certificate list in the JSON" % path)
    if not isinstance(data, list):
        raise InputError("%s: expected a JSON list of certificates" % path)
    certs = [item for item in data if isinstance(item, dict)]
    if not certs:
        raise InputError("%s: no certificate objects in the JSON" % path)
    return certs


def cert_names(cert):
    """Yield the raw names in one certificate object."""
    for key in ("name_value", "common_name"):
        value = cert.get(key)
        if isinstance(value, str):
            for line in value.splitlines():
                line = line.strip()
                if line:
                    yield line


def normalise_scope(value):
    """Return a scope domain, or raise InputError."""
    scope = value.strip().lower().rstrip(".")
    if not scope or "*" in scope or "/" in scope or " " in scope:
        raise InputError("bad --scope value: %r" % value)
    return scope


def in_scope(host, scopes):
    """True when host equals a scope domain or sits under one."""
    for scope in scopes:
        if host == scope or host.endswith("." + scope):
            return True
    return False


def load_known(path):
    """Return the known hostnames, or raise InputError."""
    if not path:
        return set()
    text = read_text(path)
    hosts = set()
    for line in text.splitlines():
        line = line.strip().lower().rstrip(".")
        if not line or line.startswith("#"):
            continue
        hosts.add(line)
    return hosts


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Diff in-scope hosts from a certificate transparency export "
                    "against a known list.")
    parser.add_argument("crt", help="crt.sh JSON export, or - for stdin")
    parser.add_argument("--scope", action="append", required=True,
                        metavar="DOMAIN",
                        help="in-scope domain; repeat for more than one")
    parser.add_argument("--known", metavar="FILE",
                        help="known hostnames, one per line; comments start with #")
    parser.add_argument("--max-list", type=int, default=DEFAULT_MAX_LIST,
                        metavar="N", help="print at most N new hosts (default 50)")
    args = parser.parse_args(argv)
    if args.max_list < 1:
        print("ct_inventory: --max-list must be at least 1", file=sys.stderr)
        return 2

    try:
        scopes = [normalise_scope(value) for value in args.scope]
        certs = load_certs(args.crt)
        known = load_known(args.known)
    except InputError as exc:
        print("ct_inventory: %s" % exc, file=sys.stderr)
        return 2

    names = 0
    wildcards = 0
    outside = 0
    malformed = 0
    seen = set()

    for cert in certs:
        for raw in cert_names(cert):
            names += 1
            name = raw.strip().lower().rstrip(".")
            if not name:
                continue
            if "*" in name:
                wildcards += 1
                continue
            if (" " in name or "/" in name or "@" in name
                    or ":" in name or name.startswith(".") or ".." in name):
                malformed += 1
                continue
            if not in_scope(name, scopes):
                outside += 1
                continue
            seen.add(name)

    if not seen:
        print("ct_inventory: no in-scope names in %s" % args.crt,
              file=sys.stderr)
        print("ct_inventory: scope was %s" % ", ".join(scopes),
              file=sys.stderr)
        return 2

    new_hosts = sorted(seen - known)
    print("CT %d certificates, %d names, %d in scope, %d wildcards, "
          "%d out of scope, %d malformed"
          % (len(certs), names, len(seen), wildcards, outside, malformed))
    if not new_hosts:
        print("OK no new hosts against %s" % (args.known or "an empty known list"))
        return 0

    print("NEW %d hosts not in %s"
          % (len(new_hosts), args.known or "an empty known list"))
    for host in new_hosts[:args.max_list]:
        print("  + %s" % host)
    if len(new_hosts) > args.max_list:
        print("  ... %d more" % (len(new_hosts) - args.max_list))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
