---
id: p735
title: "Ports that should never face the internet"
slug: ports-that-should-never-face-the-internet
sections: [devsecops]
topic: "Python scripts"
tags: [NetworkSecurity, CloudSecurity, Python, Firewalls, DevSecOps]
source: "LinkedIn post P735 · ASM series"
linkedin_date: 2031-06-08
design: code
script: port_policy.py
---

# Ports that should never face the internet

Port 3306 was opened for a migration that finished in March. In November it was still answering from the internet.

## Quick reference

The full script is at the end of this note: `port_policy.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 port_policy.py /tmp/scan.csv /tmp/policy.json
```

**Example output**

```text
FINDING 5 port-policy violations
ALERT 203.0.113.10:22 ssh admin open to 0.0.0.0/0
```

## Explained

### What it does

`port_policy.py` reads an external scan export (host, port, service, banner) and an allowed-exposure policy JSON. The scan is external, so every open port is treated as reachable from 0.0.0.0/0. A port not in the allow list is an admin port, a database port, an unknown service, or a known service on the wrong port. A blank service is inferred from the banner when possible. The fourteen lines print FINDING 5 port-policy violations and ALERT 203.0.113.10:22 ssh admin open to 0.0.0.0/0.

### How to run it

`python3 port_policy.py scan.csv policy.json`. Run it weekly from cron, or in CI after a security-group change. Exit 0 is clean, 1 is a finding, 2 is bad input.

### The fix

Close the rule in the security group, not only the host firewall. For the database, remove the public address or use a bastion. For the unknown service, identify it before you close it.

### Prevention

Generate the policy from the architecture, diff the scan against it every week, and alert on any new admin or database port. The diff is the control; the scan is only the sensor.

> **The honest caveat:** an external scan sees what the network allows, not what the application does. A port can be open on the host and filtered upstream, and banner inference is a guess when the service field is blank.

> **The lesson:** the internet does not need your database port.

## In one line

> **Close the rule, not the service.** Every open port is reachable from 0.0.0.0/0 until the rule says otherwise.

**Check from outside**

```bash
nmap -Pn -p 22,3306 203.0.113.10
```

## Script: port_policy.py

Download: [scripts/port_policy.py](../scripts/port_policy.py)

```python
#!/usr/bin/env python3
"""Compare an external port scan with the exposure policy you meant to have.

Usage:
    python3 port_policy.py scan.csv policy.json
    python3 port_policy.py scan.json policy.json --max 20

Input (an export, never a live scan):
    scan:    CSV or JSON with host, port, service, banner
    policy:  JSON:
             {
               "allow": [{"port": 80, "service": "http"},
                         {"port": 443, "service": "https"}],
               "tiers": {"ssh": "admin", "mysql": "database", ...},
               "known": ["http", "https", "ssh", "smtp", ...]
             }

The scan is external, so every open port is treated as reachable from
0.0.0.0/0. A port that the policy does not allow is reported as:
    admin     admin service open to the internet
    database  database service open to the internet
    unknown   service not in the policy's known list
    unlisted  known service, but not allowed on that port
A blank or "unknown" service is inferred from the banner when possible.

Cron/CI:
    0 5 * * 1 python3 port_policy.py /srv/exports/scan.csv /etc/exposure.json

Exit codes:
    0 every open port is allowed
    1 at least one violation
    2 bad input (unreadable file, bad JSON/CSV/policy, bad port)

Read-only: it makes no network calls and writes nothing. By s0sta.com
"""
import argparse
import csv
import io
import json
import re
import sys

ALIASES = {
    "https": "https", "ssl/https": "https", "ssl": "https", "tls": "https",
    "http": "http", "http-alt": "http", "www": "http",
    "ssh": "ssh", "openssh": "ssh",
    "domain": "dns", "dns": "dns",
    "mysql": "mysql", "mariadb": "mysql",
    "postgres": "postgresql", "postgresql": "postgresql",
    "mssql": "mssql", "ms-sql-s": "mssql",
    "redis": "redis", "mongodb": "mongodb", "mongo": "mongodb",
    "elasticsearch": "elasticsearch", "elastic": "elasticsearch",
    "rdp": "rdp", "ms-wbt-server": "rdp",
    "smtp": "smtp", "smtps": "smtp",
    "imap": "imap", "imaps": "imap",
    "pop3": "pop3", "pop3s": "pop3",
    "ftp": "ftp", "telnet": "telnet", "vnc": "vnc",
}
BLANK = ("", "unknown", "tcpwrapped", "-", "none")
RANK = {"admin": 4, "database": 3, "unknown": 2, "unlisted": 1}
REASONS = {
    "admin": "admin port open to 0.0.0.0/0",
    "database": "database port open to 0.0.0.0/0",
    "unknown": "unknown service, not in policy",
    "unlisted": "known service, not allowed",
}


def fail(message):
    print("ERROR %s" % message, file=sys.stderr)
    return 2


def norm_keys(row):
    return {str(k).strip().lower(): v for k, v in row.items() if k is not None}


def canon_service(value):
    text = str(value or "").strip().lower().replace("_", "-")
    if text in ALIASES:
        return ALIASES[text]
    token = re.split(r"[\s/]", text)[0]
    return ALIASES.get(token, token)


def parse_port(value):
    text = str(value).strip()
    if not text.isdigit():
        raise ValueError("port is not a number: %r" % text)
    port = int(text)
    if not 1 <= port <= 65535:
        raise ValueError("port out of range: %d" % port)
    return port


def infer_service(banner):
    """Best effort from a banner. A guess is labelled as the service, not proof."""
    text = str(banner or "").strip()
    low = text.lower()
    if text.startswith("SSH-"):
        return "ssh"
    if text.startswith("HTTP/") or "server:" in low:
        return "http"
    if "mysql" in low or "mariadb" in low:
        return "mysql"
    if "mongodb" in low:
        return "mongodb"
    if "redis" in low or text.startswith("-NOAUTH"):
        return "redis"
    if text.startswith("220") and "smtp" in low:
        return "smtp"
    if text.startswith("+OK"):
        return "pop3"
    if text.startswith("* OK"):
        return "imap"
    if "postgres" in low:
        return "postgresql"
    return "unknown"


def load_policy(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ValueError("cannot read policy %s: %s" % (path, exc))
    except ValueError as exc:
        raise ValueError("bad JSON in policy %s: %s" % (path, exc))
    if not isinstance(data, dict):
        raise ValueError("policy must be a JSON object")
    allow = data.get("allow")
    if not isinstance(allow, list) or not allow:
        raise ValueError("policy needs a non-empty allow list")
    rules = []
    for i, item in enumerate(allow, 1):
        if not isinstance(item, dict):
            raise ValueError("allow entry %d is not an object" % i)
        port = item.get("port")
        service = item.get("service")
        if port is None and service is None:
            raise ValueError("allow entry %d needs a port or a service" % i)
        try:
            port = parse_port(port) if port is not None else None
        except ValueError as exc:
            raise ValueError("allow entry %d: %s" % (i, exc))
        service = canon_service(service) if service not in (None, "*") else "*"
        rules.append((port, service))

    tiers = data.get("tiers") or {}
    if not isinstance(tiers, dict):
        raise ValueError("policy tiers must be an object")
    tiers = {canon_service(k): str(v).lower() for k, v in tiers.items()}
    for key in ("admin_services", "database_services", "known"):
        if key in data and not isinstance(data[key], list):
            raise ValueError("policy %s must be a list" % key)
    for service in data.get("admin_services", []):
        tiers.setdefault(canon_service(service), "admin")
    for service in data.get("database_services", []):
        tiers.setdefault(canon_service(service), "database")
    bad = [s for s, tier in tiers.items() if tier not in ("admin", "database")]
    if bad:
        raise ValueError("tiers must be admin or database, not %s" % ", ".join(bad))

    known = {canon_service(s) for s in data.get("known", [])}
    if not known:
        known = set(tiers)
        known.update(service for _port, service in rules if service != "*")
    return rules, tiers, known


def load_scan(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
    except OSError as exc:
        raise ValueError("cannot read scan %s: %s" % (path, exc))
    if not raw.strip():
        raise ValueError("empty input: %s" % path)

    if raw.lstrip().startswith(("[", "{")):
        try:
            data = json.loads(raw)
        except ValueError as exc:
            raise ValueError("bad JSON in scan %s: %s" % (path, exc))
        if isinstance(data, dict):
            for key in ("hosts", "scan", "results", "items"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
            else:
                raise ValueError("JSON object has no hosts/scan/results list")
        if not isinstance(data, list):
            raise ValueError("scan must be a list or an object with a hosts list")
        rows = []
        for i, row in enumerate(data, 1):
            if not isinstance(row, dict):
                raise ValueError("host %d is not an object" % i)
            rows.append(normalise(norm_keys(row), i))
        return rows

    reader = csv.DictReader(io.StringIO(raw))
    fields = [str(f).strip().lower() for f in (reader.fieldnames or [])]
    if "host" not in fields or "port" not in fields:
        raise ValueError("CSV needs host and port columns, got %s" % fields)
    return [normalise(norm_keys(row), i + 2) for i, row in enumerate(reader)]


def normalise(row, line_no):
    host = str(row.get("host") or "").strip()
    if not host:
        raise ValueError("row %d has no host" % line_no)
    try:
        port = parse_port(row.get("port"))
    except ValueError as exc:
        raise ValueError("row %d (%s): %s" % (line_no, host, exc))
    service = canon_service(row.get("service"))
    banner = str(row.get("banner") or "").strip()
    if service in BLANK:
        service = infer_service(banner)
    return {"host": host, "port": port, "service": service, "banner": banner}


def allowed(port, service, rules):
    for rule_port, rule_service in rules:
        if rule_port is not None and rule_port != port:
            continue
        if rule_service not in (None, "*") and rule_service != service:
            continue
        return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare an external port scan with an exposure policy.",
        epilog="Every open port is treated as reachable from 0.0.0.0/0.")
    parser.add_argument("scan", help="scan export: CSV or JSON")
    parser.add_argument("policy", help="allowed-exposure policy: JSON")
    parser.add_argument("--max", type=int, default=100,
                        help="show at most N violations (default: 100)")
    args = parser.parse_args(argv)
    if args.max < 1:
        return fail("--max must be at least 1")

    try:
        rules, tiers, known = load_policy(args.policy)
        rows = load_scan(args.scan)
    except ValueError as exc:
        return fail(str(exc))

    found = []
    for row in rows:
        if allowed(row["port"], row["service"], rules):
            continue
        tier = tiers.get(row["service"])
        if tier in ("admin", "database"):
            kind = tier
        elif row["service"] == "unknown" or row["service"] not in known:
            kind = "unknown"
        else:
            kind = "unlisted"
        found.append((RANK[kind], row["host"], row["port"], row["service"], kind))
    found.sort(key=lambda item: (-item[0], item[1], item[2]))

    if not found:
        hosts = len({row["host"] for row in rows})
        word = "host" if hosts == 1 else "hosts"
        print("OK all %d open ports are allowed on %d %s" % (len(rows), hosts, word))
        return 0

    hosts = len({item[1] for item in found})
    print("FINDING %d port-policy violations on %d hosts" % (len(found), hosts))
    for _rank, host, port, service, kind in found[:args.max]:
        print("ALERT %s:%d %s %s" % (host, port, service, REASONS[kind]))
    if len(found) > args.max:
        print("NOTE %d more violations not shown" % (len(found) - args.max))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
