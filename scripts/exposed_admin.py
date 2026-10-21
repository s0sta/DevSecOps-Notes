#!/usr/bin/env python3
"""Rank admin and login panels that an HTTP probe saw reachable.

Usage:
    python3 exposed_admin.py probe.json
    python3 exposed_admin.py probe.csv --top 5

Input (an export, never a live request):
    JSON: [{"url": "...", "status": 200, "title": "Jenkins",
            "headers": {"server": "nginx"}}, ...]
          or {"probes": [...]} / {"results": [...]}
    CSV:  url,status,title,headers
          headers may be a JSON object or "Key: Value; Key2: Value2".

Reachable means status 200 and no WWW-Authenticate challenge. The score is
the product weight plus 20 for an open response, and the two factors are
printed so the number is traceable:
    admin 40, jenkins 38, grafana 36, phpmyadmin 34, login 20.

Cron/CI:
    0 6 * * * python3 exposed_admin.py /srv/exports/http-probe.json

Exit codes:
    0 no reachable admin or login panel
    1 at least one reachable panel
    2 bad input (unreadable file, bad JSON/CSV, missing url or status)

Read-only: it makes no network calls and writes nothing. By s0sta.com
"""
import argparse
import csv
import io
import json
import sys

BASE = {"admin": 40, "jenkins": 38, "grafana": 36, "phpmyadmin": 34, "login": 20}
OPEN_BONUS = 20
ADMIN_HINTS = ("/admin", "admin", "administrator", "wp-admin", "manager/html",
               "adminer", "console")
LOGIN_HINTS = ("login", "log in", "signin", "sign-in", "sign in", "auth")
PRODUCTS = ("jenkins", "grafana", "phpmyadmin")


def fail(message):
    """Bad input is exit 2, never a silent pass."""
    print("ERROR %s" % message, file=sys.stderr)
    return 2


def norm_keys(row):
    return {str(k).strip().lower(): v for k, v in row.items() if k is not None}


def parse_status(value):
    text = str(value).strip()
    if not text:
        raise ValueError("empty status")
    head = text.split()[0]
    if not head.isdigit():
        raise ValueError("status is not a number: %r" % text)
    return int(head)


def parse_headers(value):
    """Return a lower-case header map. Unparseable headers are not fatal."""
    if isinstance(value, dict):
        return {str(k).lower(): str(v) for k, v in value.items()}
    text = str(value or "").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    if isinstance(data, dict):
        return {str(k).lower(): str(v) for k, v in data.items()}
    out = {}
    for part in text.replace("\n", ";").split(";"):
        if ":" in part:
            key, val = part.split(":", 1)
            out[key.strip().lower()] = val.strip()
    return out


def load(path):
    """Read JSON or CSV and return a list of normalised probe rows."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    if not raw.strip():
        raise ValueError("empty input: %s" % path)

    if raw.lstrip().startswith(("[", "{")):
        try:
            data = json.loads(raw)
        except ValueError as exc:
            raise ValueError("bad JSON in %s: %s" % (path, exc))
        if isinstance(data, dict):
            for key in ("probes", "results", "items"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
            else:
                raise ValueError("JSON object has no probes/results list")
        if not isinstance(data, list):
            raise ValueError("JSON must be a list or an object with a probes list")
        rows = []
        for i, row in enumerate(data, 1):
            if not isinstance(row, dict):
                raise ValueError("probe %d is not an object" % i)
            rows.append(normalise(norm_keys(row), i))
        return rows

    reader = csv.DictReader(io.StringIO(raw))
    fields = [str(f).strip().lower() for f in (reader.fieldnames or [])]
    if "url" not in fields or "status" not in fields:
        raise ValueError("CSV needs url and status columns, got %s" % fields)
    return [normalise(norm_keys(row), i + 2) for i, row in enumerate(reader)]


def normalise(row, line_no):
    url = str(row.get("url") or "").strip()
    if not url:
        raise ValueError("row %d has no url" % line_no)
    try:
        status = parse_status(row.get("status", row.get("http_status", "")))
    except ValueError as exc:
        raise ValueError("row %d (%s): %s" % (line_no, url, exc))
    title = str(row.get("title") or "").strip()
    headers = parse_headers(row.get("headers", ""))
    return {"url": url, "status": status, "title": title, "headers": headers}


def product(url, title):
    """Classify a panel. Specific products win before the generic admin match."""
    hay = (url + " " + title).lower()
    for name in PRODUCTS:
        if name in hay:
            return name
    if any(hint in hay for hint in ADMIN_HINTS):
        return "admin"
    if any(hint in hay for hint in LOGIN_HINTS):
        return "login"
    return ""


def reachable(row):
    """200 alone is not enough: a Basic challenge means the panel is gated."""
    return row["status"] == 200 and "www-authenticate" not in row["headers"]


def score(kind):
    return BASE[kind] + OPEN_BONUS


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rank admin and login panels reachable without auth.",
        epilog="Reads an HTTP probe export (JSON or CSV). Exit 1 on a finding.")
    parser.add_argument("probe", help="HTTP probe export: JSON or CSV")
    parser.add_argument("--top", type=int, default=10,
                        help="show at most N panels (default: 10)")
    args = parser.parse_args(argv)
    if args.top < 1:
        return fail("--top must be at least 1")
    try:
        rows = load(args.probe)
    except ValueError as exc:
        return fail(str(exc))

    found = []
    for row in rows:
        kind = product(row["url"], row["title"])
        if kind and reachable(row):
            found.append((score(kind), kind, row))
    found.sort(key=lambda item: (-item[0], item[2]["url"]))

    word = "probe" if len(rows) == 1 else "probes"
    if not found:
        print("OK no reachable admin or login panel in %d %s" % (len(rows), word))
        return 0

    print("FINDING %d reachable panels of %d %s" % (len(found), len(rows), word))
    for total, kind, row in found[:args.top]:
        print("ALERT %d %s %d %s [%d+%d]"
              % (total, kind, row["status"], row["url"], BASE[kind], OPEN_BONUS))
    if len(found) > args.top:
        print("NOTE %d more panels not shown" % (len(found) - args.top))
    return 1


if __name__ == "__main__":
    sys.exit(main())
