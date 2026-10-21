#!/usr/bin/env python3
"""Audit a lockfile for supply-chain risk: hashes, hosts and sources.

Reads a package-lock.json (lockfileVersion 2 or 3) or a generic JSON
mapping package paths to entries, then flags:
  - an entry with no integrity hash (the SRI string npm writes
    for registry packages)
  - a resolved URL whose host is not an allowed registry
  - a resolved source that is a file: or git: reference

Usage:
    python3 lockfile_audit.py package-lock.json
    python3 lockfile_audit.py package-lock.json --allow-host npm.acme.internal
    python3 lockfile_audit.py package-lock.json --json

The default registry host is registry.npmjs.org. Add private registries
with --allow-host; the flag may be repeated. The lockfile is only read,
never changed. Bundled dependencies, workspace links and local links have
no integrity hash by design, so they are reported rather than skipped.

Exit codes:
    0  every entry has an integrity hash and an allowed registry source
    1  at least one finding
    2  usage error, or a lockfile that is missing, unreadable or invalid

Cron: 0 6 * * 1 python3 lockfile_audit.py package-lock.json
CI:   python3 lockfile_audit.py package-lock.json --allow-host "$NPM_HOST"

By s0sta.com
"""

import argparse
import json
import sys
from urllib.parse import urlparse

DEFAULT_HOSTS = ("registry.npmjs.org",)
FILE_PREFIX = ("file:",)
GIT_PREFIXES = ("git+", "git:", "github:", "gitlab:", "bitbucket:", "gist:")


class LockfileError(Exception):
    """The input cannot be used as a lockfile."""


def load_json(path):
    """Return the parsed JSON document, or raise LockfileError."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise LockfileError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise LockfileError("%s is not valid JSON: %s" % (path, exc))


def walk_dependencies(deps, prefix=""):
    """Yield (path, entry) for a v1 dependencies tree, depth first."""
    for name, entry in deps.items():
        if not isinstance(entry, dict):
            raise LockfileError("%s is not an object" % name)
        if prefix:
            path = prefix + "/node_modules/" + name
        else:
            path = "node_modules/" + name
        yield path, entry
        nested = entry.get("dependencies")
        if isinstance(nested, dict):
            for item in walk_dependencies(nested, path):
                yield item


def package_entries(doc):
    """Return a list of (path, entry) pairs from any supported document."""
    if isinstance(doc, list):
        items = []
        for index, entry in enumerate(doc, 1):
            if not isinstance(entry, dict):
                raise LockfileError("entry %d is not an object" % index)
            path = entry.get("path") or entry.get("name")
            if not isinstance(path, str) or not path:
                raise LockfileError("entry %d has no path or name" % index)
            items.append((path, entry))
    elif isinstance(doc, dict):
        packages = doc.get("packages")
        if isinstance(packages, dict):
            items = list(packages.items())
        elif isinstance(doc.get("dependencies"), dict):
            items = list(walk_dependencies(doc["dependencies"]))
        else:
            items = list(doc.items())
    else:
        raise LockfileError("expected a JSON object or list")

    entries = []
    for path, entry in items:
        if path == "":
            continue
        if not isinstance(path, str) or not path:
            raise LockfileError("invalid package path %r" % (path,))
        if not isinstance(entry, dict):
            raise LockfileError("%s is not an object" % path)
        entries.append((path, entry))
    if not entries:
        raise LockfileError("no package entries found")
    return entries


def source_kind(resolved):
    """Classify a resolved value as file, git, url or other."""
    text = resolved.strip().lower()
    if text.startswith(FILE_PREFIX):
        return "file"
    if text.startswith(GIT_PREFIXES):
        return "git"
    if text.startswith(("http://", "https://")):
        return "url"
    return "other"


def audit_entry(path, entry, allowed_hosts):
    """Return the list of reasons this entry is risky."""
    reasons = []
    integrity = entry.get("integrity")
    if not isinstance(integrity, str) or not integrity.strip():
        reasons.append("no integrity hash")

    resolved = entry.get("resolved")
    if resolved is not None and not isinstance(resolved, str):
        raise LockfileError("%s has a non-string resolved value" % path)
    if resolved:
        kind = source_kind(resolved)
        if kind == "file":
            reasons.append("file: source")
        elif kind == "git":
            reasons.append("git source")
        elif kind == "url":
            host = urlparse(resolved).hostname
            if not host:
                reasons.append("URL without a host")
            elif host.lower() not in allowed_hosts:
                reasons.append("non-registry host: %s" % host)
        else:
            reasons.append("unrecognised source: %s" % resolved)
    return reasons


def audit(path, allowed_hosts):
    """Return (entry_count, findings) for a lockfile path."""
    doc = load_json(path)
    entries = package_entries(doc)
    findings = []
    for package_path, entry in entries:
        reasons = audit_entry(package_path, entry, allowed_hosts)
        if reasons:
            findings.append((package_path, reasons))
    findings.sort(key=lambda item: item[0])
    return len(entries), findings


def plural(count, word):
    """Return a count and a correctly pluralised noun."""
    return "%d %s%s" % (count, word, "" if count == 1 else "s")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit a package-lock.json for supply-chain risk.",
        epilog="Exit 0 clean, 1 finding, 2 usage or input error. By s0sta.com")
    parser.add_argument("lockfile", help="package-lock.json or generic JSON")
    parser.add_argument("--allow-host", action="append", default=[], metavar="HOST",
                        help="extra registry host to accept (repeatable)")
    parser.add_argument("--json", action="store_true",
                        help="print the findings as JSON")
    args = parser.parse_args(argv)

    allowed = {host.lower() for host in DEFAULT_HOSTS}
    for host in args.allow_host:
        host = host.strip().lower()
        if not host:
            parser.error("--allow-host cannot be empty")
        allowed.add(host)

    try:
        checked, findings = audit(args.lockfile, allowed)
    except LockfileError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    if args.json:
        payload = {
            "lockfile": args.lockfile,
            "packages": checked,
            "ok": not findings,
            "findings": [{"path": p, "reasons": r} for p, r in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for package_path, reasons in findings:
            print("RISK %s: %s" % (package_path, ", ".join(reasons)))
        if findings:
            issues = sum(len(reasons) for _, reasons in findings)
            print("FAIL %s with findings, %s"
                  % (plural(len(findings), "package"), plural(issues, "issue")))
        else:
            print("OK %s checked" % plural(checked, "package"))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
