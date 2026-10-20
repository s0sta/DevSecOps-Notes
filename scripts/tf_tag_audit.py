#!/usr/bin/env python3
"""tf_tag_audit.py - fail a Terraform plan when changed resources lack tags.

Reads the JSON that `terraform show -json` prints for a saved plan and checks
every managed resource the plan creates or replaces or updates. A resource
passes when its planned tags (or tags_all, which includes provider default
tags) carry every required name. Resource types that do not expose tags in
the plan are counted and skipped.

Usage:
    terraform plan -out plan.out
    terraform show -json plan.out > /tmp/plan.json
    python3 tf_tag_audit.py /tmp/plan.json
    terraform show -json plan.out | python3 tf_tag_audit.py -
    python3 tf_tag_audit.py /tmp/plan.json --require Owner,Team,Environment
    python3 tf_tag_audit.py /tmp/plan.json -q

Exit codes: 0 clean, 1 required tags missing, 2 usage or input error.

CI (run it after terraform plan, before apply):
    terraform plan -out plan.out && \
        terraform show -json plan.out > /tmp/plan.json && \
        python3 tf_tag_audit.py /tmp/plan.json

Read-only: it reads one JSON document and writes nothing. Standard library
only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys

REQUIRED = ("Owner", "Environment", "CostCenter")
CHANGED = ("create", "update")


class CheckError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source):
    """Read one JSON document from a file or '-' for stdin."""
    if source == "-":
        try:
            return json.load(sys.stdin)
        except ValueError as exc:
            raise CheckError("stdin is not JSON: %s" % exc)
    try:
        with open(source) as handle:
            return json.load(handle)
    except OSError as exc:
        raise CheckError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise CheckError("%s is not JSON: %s" % (source, exc))


def audit(doc, required):
    """Return (findings, checked, skipped) for one plan document."""
    if not isinstance(doc, dict):
        raise CheckError("plan must be a JSON object")
    changes = doc.get("resource_changes")
    if changes is None:
        raise CheckError("no resource_changes: pass plan JSON, not state JSON")
    if not isinstance(changes, list):
        raise CheckError("resource_changes must be a list")

    findings = []
    checked = 0
    skipped = 0
    for item in changes:
        if not isinstance(item, dict):
            raise CheckError("every resource_changes entry must be an object")
        if item.get("mode", "managed") != "managed":
            continue
        change = item.get("change")
        if not isinstance(change, dict):
            raise CheckError("resource_changes entry has no change object")
        actions = change.get("actions") or []
        if not isinstance(actions, list):
            raise CheckError("change.actions must be a list")
        if not set(CHANGED) & set(actions):
            continue
        after = change.get("after")
        if not isinstance(after, dict):
            continue
        if "tags" not in after and "tags_all" not in after:
            skipped += 1
            continue
        tags = after.get("tags_all")
        if not isinstance(tags, dict):
            tags = after.get("tags")
        if tags is None:
            tags = {}
        if not isinstance(tags, dict):
            raise CheckError("tags for %s are not an object" % item.get("address", "?"))
        checked += 1
        missing = sorted(set(required) - set(tags))
        if missing:
            address = item.get("address") or item.get("type") or "(unknown)"
            findings.append((address, missing))
    return findings, checked, skipped


def parse_required(raw):
    """Turn 'Owner, Environment' into ('Owner', 'Environment')."""
    names = tuple(name.strip() for name in raw.split(",") if name.strip())
    if not names:
        raise ValueError("no tag names given")
    return names


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Fail when a Terraform plan changes resources without the required tags.",
        epilog="Exit codes: 0 clean, 1 missing tags, 2 usage or input error.")
    parser.add_argument("plan", help="plan JSON from terraform show -json, or - for stdin")
    parser.add_argument("-r", "--require", default=",".join(REQUIRED), metavar="TAGS",
                        help="comma-separated tag names, default %s" % ",".join(REQUIRED))
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args(argv)

    try:
        required = parse_required(args.require)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        findings, checked, skipped = audit(read_json(args.plan), required)
    except CheckError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if findings:
        if not args.quiet:
            for address, missing in findings:
                print("ERR %s missing %s" % (address, ",".join(missing)))
        plural = "" if len(findings) == 1 else "s"
        print("ERR %d resource%s missing required tags (%d checked, %d untaggable)"
              % (len(findings), plural, checked, skipped))
        return 1

    print("OK %d changed resource%s carry %s (%d untaggable skipped)"
          % (checked, "" if checked == 1 else "s", ", ".join(required), skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
