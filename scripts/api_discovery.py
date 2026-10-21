#!/usr/bin/env python3
"""Diff an OpenAPI spec against the routes a gateway actually serves.

Usage:
    python3 api_discovery.py openapi.json routes.csv
    python3 api_discovery.py specs.json routes.json --max 20

Input (exports, never a live gateway call):
    spec:    one OpenAPI 2/3 document, a list of documents, or {"specs": [...]}
    routes:  CSV or JSON with method, path and optional public (true/false)

Flags:
    admin         admin-looking path with no security requirement
    no-security   no global or operation security declared
    undocumented  routed, but absent from every spec
    deprecated    deprecated in the spec and still routed

A route marked public in the inventory is exempt from the auth flags: a
health check is meant to be public. A deprecated route is flagged whether
or not it has auth. When two specs declare the same method and path, the
first spec in the file wins, so put the authoritative one first.

Cron/CI:
    0 6 * * * python3 api_discovery.py openapi.json /srv/exports/routes.csv

Exit codes:
    0 no exposure
    1 at least one exposed endpoint
    2 bad input (unreadable file, bad JSON/CSV, missing method/path, bad public)

Read-only: it makes no network calls and writes nothing. By s0sta.com
"""
import argparse
import csv
import io
import json
import re
import sys
from urllib.parse import urlparse

METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")
ADMIN_SEGMENTS = {"admin", "administrator", "internal", "manage", "management",
                  "debug", "actuator", "console", "private", "staff", "system"}
RANK = {"admin": 4, "no-security": 3, "undocumented": 2, "deprecated": 1}


def fail(message):
    print("ERROR %s" % message, file=sys.stderr)
    return 2


def norm_keys(row):
    return {str(k).strip().lower(): v for k, v in row.items() if k is not None}


def as_bool(value):
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in ("", "false", "0", "no", "off"):
        return False
    if text in ("true", "1", "yes", "on"):
        return True
    raise ValueError("not a boolean: %r" % str(value))


def norm_path(value):
    text = str(value or "").strip()
    text = text.split("?")[0].split("#")[0]
    if not text.startswith("/"):
        text = "/" + text
    if len(text) > 1:
        text = text.rstrip("/")
    return text


def path_regex(path):
    parts = re.split(r"(\{[^}]+\})", path)
    body = "".join("[^/]+" if part.startswith("{") else re.escape(part)
                   for part in parts)
    return re.compile("^" + body + "$")


def spec_name(doc, index):
    info = doc.get("info") if isinstance(doc.get("info"), dict) else {}
    title = str(info.get("title") or "").strip()
    return title or "spec %d" % index


def base_path(doc):
    servers = doc.get("servers")
    if isinstance(servers, list) and servers and isinstance(servers[0], dict):
        url = str(servers[0].get("url") or "")
        return urlparse(url).path.rstrip("/")
    return str(doc.get("basePath") or "").rstrip("/")


def load_specs(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ValueError("cannot read spec %s: %s" % (path, exc))
    except ValueError as exc:
        raise ValueError("bad JSON in spec %s: %s" % (path, exc))

    if isinstance(data, dict) and isinstance(data.get("specs"), list):
        data = data["specs"]
    elif isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data:
        raise ValueError("spec must be an object, a list, or {specs: [...]}")
    specs = []
    for i, doc in enumerate(data, 1):
        if not isinstance(doc, dict) or not isinstance(doc.get("paths"), dict):
            raise ValueError("spec %d has no paths object" % i)
        specs.append((spec_name(doc, i), doc))
    return specs


def build_routes(specs):
    routes = []
    seen = set()
    for name, doc in specs:
        base = base_path(doc)
        for template, item in doc["paths"].items():
            if not isinstance(item, dict):
                continue
            for method in METHODS:
                op = item.get(method)
                if not isinstance(op, dict):
                    continue
                for prefix in (base, ""):
                    full = norm_path(str(prefix) + str(template))
                    key = (method, full)
                    if key in seen:
                        continue
                    seen.add(key)
                    routes.append({
                        "method": method,
                        "path": full,
                        "regex": path_regex(full),
                        "op": op,
                        "doc": doc,
                        "spec": name,
                    })
    return routes


def load_routes(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
    except OSError as exc:
        raise ValueError("cannot read routes %s: %s" % (path, exc))
    if not raw.strip():
        raise ValueError("empty input: %s" % path)

    if raw.lstrip().startswith(("[", "{")):
        try:
            data = json.loads(raw)
        except ValueError as exc:
            raise ValueError("bad JSON in routes %s: %s" % (path, exc))
        if isinstance(data, dict):
            for key in ("routes", "endpoints", "items"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
            else:
                raise ValueError("JSON object has no routes/endpoints list")
        if not isinstance(data, list):
            raise ValueError("routes must be a list or an object with a routes list")
        rows = []
        for i, row in enumerate(data, 1):
            if not isinstance(row, dict):
                raise ValueError("route %d is not an object" % i)
            rows.append(normalise(norm_keys(row), i))
        return rows

    reader = csv.DictReader(io.StringIO(raw))
    fields = [str(f).strip().lower() for f in (reader.fieldnames or [])]
    if "method" not in fields or "path" not in fields:
        raise ValueError("CSV needs method and path columns, got %s" % fields)
    return [normalise(norm_keys(row), i + 2) for i, row in enumerate(reader)]


def normalise(row, line_no):
    method = str(row.get("method") or "").strip()
    path = str(row.get("path") or "").strip()
    if not method:
        raise ValueError("row %d has no method" % line_no)
    if not path:
        raise ValueError("row %d has no path" % line_no)
    try:
        public = as_bool(row.get("public"))
    except ValueError as exc:
        raise ValueError("row %d (%s %s): %s" % (line_no, method, path, exc))
    return {"method": method.upper(), "path": norm_path(path), "public": public}


def has_security(op, doc):
    """[] is explicit public; [{}] is an anonymous alternative, so also public."""
    sec = op["security"] if "security" in op else doc.get("security")
    if not isinstance(sec, list) or not sec:
        return False
    return all(isinstance(req, dict) and bool(req) for req in sec)


def schemes(doc):
    components = doc.get("components")
    if isinstance(components, dict) and isinstance(components.get("securitySchemes"), dict):
        return components["securitySchemes"]
    definitions = doc.get("securityDefinitions")
    return definitions if isinstance(definitions, dict) else {}


def is_admin(path):
    return any(segment in ADMIN_SEGMENTS for segment in path.lower().split("/"))


def classify(route, public, path):
    admin = is_admin(path)
    if route is None:
        return (["admin"] if admin else []) + ["undocumented"]
    op, doc = route["op"], route["doc"]
    secured = has_security(op, doc)
    flags = []
    if admin and not secured and not public:
        flags.append("admin")
    if not secured and not public:
        flags.append("no-security")
    if op.get("deprecated") is True:
        flags.append("deprecated")
    return flags


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Diff an OpenAPI spec against a gateway route inventory.",
        epilog="Flags auth gaps, admin routes, undocumented routes and routed deprecations.")
    parser.add_argument("spec", help="OpenAPI spec: JSON")
    parser.add_argument("routes", help="endpoint inventory: CSV or JSON")
    parser.add_argument("--max", type=int, default=100,
                        help="show at most N endpoints (default: 100)")
    args = parser.parse_args(argv)
    if args.max < 1:
        return fail("--max must be at least 1")

    try:
        specs = load_specs(args.spec)
        inventory = load_routes(args.routes)
    except ValueError as exc:
        return fail(str(exc))

    for name, doc in specs:
        if not schemes(doc):
            print("WARN spec %r defines no securitySchemes" % name)

    routes = build_routes(specs)
    found = []
    for endpoint in inventory:
        match = None
        for route in routes:
            if route["method"] == endpoint["method"].lower() and \
                    route["regex"].match(endpoint["path"]):
                match = route
                break
        if match is None:
            flags = classify(None, endpoint["public"], endpoint["path"])
        else:
            flags = classify(match, endpoint["public"], endpoint["path"])
        if flags:
            rank = max(RANK[flag] for flag in flags)
            found.append((rank, endpoint["method"], endpoint["path"], flags))
    found.sort(key=lambda item: (-item[0], item[1], item[2]))

    if not found:
        print("OK no exposed endpoint in %d routed" % len(inventory))
        return 0

    print("FINDING %d exposed endpoints of %d routed" % (len(found), len(inventory)))
    for _rank, method, path, flags in found[:args.max]:
        print("ALERT %s %s %s" % (method, path, ",".join(flags)))
    if len(found) > args.max:
        print("NOTE %d more endpoints not shown" % (len(found) - args.max))
    return 1


if __name__ == "__main__":
    sys.exit(main())
