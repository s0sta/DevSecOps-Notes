---
id: p559
title: "An OpenAPI auth check in Python"
slug: an-openapi-auth-check-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [OpenAPI, API, Python, DevSecOps, AppSec]
source: "LinkedIn post P559 · PythonSec series"
linkedin_date: 2030-04-23
design: code
script: openapi_auth_check.py
---

# An OpenAPI auth check in Python

Every API has one endpoint nobody remembers. It is in the gateway, missing from the spec, and it is the one that accepts anonymous writes.

## Quick reference

The full script is at the end of this note: `openapi_auth_check.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 openapi_auth_check.py api.json
```

**Example output**

```text
FAIL 2 unauthenticated operation(s)
GET /health, GET /v1/reports
```

## Explained

### What it reads

The script loads an OpenAPI 3 JSON document and walks every path and method. For each operation it takes the security list from the operation itself, or inherits the root list when the operation has none. The output names the method and the path, so every fix has a one-line address. A path item behind a $ref is skipped, not guessed.

### What it flags

No security at either level is a gap. So is security: [], a deliberate public endpoint, and security: [{}], an empty requirement that makes auth optional in the OpenAPI model. The `--allow` flag accepts the public endpoints you meant to ship, by path or by method and path.

### The run

On the sample spec it prints two lines: FAIL 2 unauthenticated operation(s), then GET /health, GET /v1/reports, and exits 1. A spec where every operation inherits bearerAuth exits 0. A file that is not JSON, or not OpenAPI 3, exits 2. The full script is attached, standard library only and read-only.

> **The honest caveat:** this checks declarations, not enforcement. An operation can declare bearerAuth and still accept anonymous traffic if the handler forgets the check, so pair it with a request test against a real token.

> **The lesson:** a spec that hides an endpoint cannot secure it.

## In one line

> **Declared is not enforced.** A spec that hides an endpoint cannot protect it.

**Allow the public**

```bash
python3 openapi_auth_check.py --allow /health
```

## Script: openapi_auth_check.py

Download: [scripts/openapi_auth_check.py](../scripts/openapi_auth_check.py)

```python
#!/usr/bin/env python3
"""Check an OpenAPI 3 document for operations with no auth requirement.

Reads the JSON spec, walks every path and method, and reports each operation
that does not require authentication. Security can be declared once at the
document root or per operation; per-operation security replaces the global
list, so an explicit empty list is a deliberate public endpoint and an empty
requirement object ({}) makes auth optional. Both are still reported.

Use --allow to accept an intended public endpoint, by path ("/health") or by
method and path ("GET /health"). Allowed endpoints are counted but not
reported.

Usage:
    python3 openapi_auth_check.py /tmp/openapi.json
    python3 openapi_auth_check.py /tmp/openapi.json --allow /health
    python3 openapi_auth_check.py /tmp/openapi.json --allow "POST /login"
    python3 openapi_auth_check.py /tmp/openapi.json --verbose
    python3 openapi_auth_check.py --help

CI (before publishing a spec):
    python3 openapi_auth_check.py api/openapi.json || exit 1

Cron (daily at 07:00, to catch a spec committed after hours):
    0 7 * * * python3 /opt/s0sta/openapi_auth_check.py /srv/api/openapi.json

Exit codes: 0 every operation requires auth, 1 at least one does not,
2 usage or unreadable input.
Read-only: the file is read, nothing is written, nothing is fetched.

JSON only. Convert a YAML spec first with the tool your CI already uses;
the script rejects text that is not JSON with exit 2.

The honest limit: this reads declarations, not enforcement. An operation
can declare bearerAuth and still accept anonymous traffic if the handler
forgets the check, so pair this with a request test.

By s0sta.com
"""
import argparse
import json
import sys

METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


def load_spec(path):
    """Read and shape-check one OpenAPI 3 JSON document."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            spec = json.load(handle)
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    except json.JSONDecodeError as exc:
        raise ValueError("%s is not valid JSON (JSON only, not YAML): %s"
                         % (path, exc))

    if not isinstance(spec, dict):
        raise ValueError("the spec must be a JSON object")
    if "swagger" in spec and "openapi" not in spec:
        raise ValueError("OpenAPI 2 (swagger) is not supported; use 3.x")
    version = spec.get("openapi")
    if not isinstance(version, str) or not version.startswith("3."):
        raise ValueError("the spec has no openapi 3.x version field")
    if not isinstance(spec.get("paths"), dict):
        raise ValueError("the spec has no paths object")
    security = spec.get("security")
    if security is not None and not isinstance(security, list):
        raise ValueError("the global security field must be a list")
    return spec


def check_security(security):
    """Validate one security list and return its gap reason, or None."""
    if not isinstance(security, list):
        raise ValueError("a security field must be a list")
    for requirement in security:
        if not isinstance(requirement, dict):
            raise ValueError("each security requirement must be an object")
    if not security:
        return "security is an empty list"
    if any(not requirement for requirement in security):
        return "an empty requirement ({}) makes auth optional"
    return None


def collect(spec):
    """Return (operations, gaps) where gaps are (method, path, reason)."""
    global_security = spec.get("security")
    operations = 0
    gaps = []
    refs = 0
    for path, item in spec["paths"].items():
        if not isinstance(item, dict):
            raise ValueError("path %r must be an object" % path)
        if "$ref" in item:
            refs += 1
            continue
        for method in METHODS:
            if method not in item:
                continue
            operation = item[method]
            if not isinstance(operation, dict):
                raise ValueError("%s %s must be an object" % (method.upper(), path))
            operations += 1
            if "security" in operation:
                security = operation["security"]
                source = "operation"
            else:
                security = global_security
                source = "global"
            if security is None:
                gaps.append((method, path, "no security at operation or global level"))
                continue
            reason = check_security(security)
            if reason:
                gaps.append((method, path, "%s: %s" % (source, reason)))
    return operations, gaps, refs


def allowed_match(allowed, method, path):
    """True when a gap is on the --allow list."""
    target = "%s %s" % (method.upper(), path)
    return target in allowed or path in allowed


def build_parser():
    """Return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="openapi_auth_check.py",
        description="Report OpenAPI 3 operations that do not require "
                    "authentication, from the global security list or the "
                    "operation's own. Exits 1 when any operation is open.")
    parser.add_argument("spec", metavar="JSON",
                        help="OpenAPI 3 document in JSON form")
    parser.add_argument("--allow", action="append", default=[],
                        metavar="PATH",
                        help='intended public endpoint, by path or by '
                             '"METHOD /path"; repeatable')
    parser.add_argument("--verbose", action="store_true",
                        help="print one line of detail per gap")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    allowed = set()
    for entry in args.allow:
        parts = entry.split()
        if len(parts) == 2:
            allowed.add("%s %s" % (parts[0].upper(), parts[1]))
        elif len(parts) == 1:
            allowed.add(parts[0])
        else:
            print("ERROR --allow takes /path or 'METHOD /path'", file=sys.stderr)
            return 2

    try:
        spec = load_spec(args.spec)
        operations, gaps, refs = collect(spec)
    except ValueError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    open_gaps = []
    allowed_count = 0
    for method, path, reason in gaps:
        if allowed_match(allowed, method, path):
            allowed_count += 1
            continue
        open_gaps.append((method, path, reason))

    if open_gaps:
        print("FAIL %d unauthenticated operation(s)" % len(open_gaps))
        print(", ".join("%s %s" % (method.upper(), path)
                        for method, path, _ in open_gaps))
        if args.verbose:
            for method, path, reason in open_gaps:
                print("  %s %s: %s" % (method.upper(), path, reason))
        return 1

    note = ""
    if allowed_count:
        note = "; %d allowed" % allowed_count
    if refs:
        note += "; %d path item(s) behind $ref" % refs
    print("OK %d operation(s), all require auth%s" % (operations, note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
