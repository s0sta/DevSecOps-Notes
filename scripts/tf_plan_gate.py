#!/usr/bin/env python3
"""tf_plan_gate.py - fail a pipeline when a Terraform plan deletes or replaces.

Reads the JSON printed by `terraform show -json` and walks
resource_changes[].change.actions. Terraform writes:

    ["no-op"] ["create"] ["update"] ["read"]
    ["delete"]                     a plain destroy
    ["delete", "create"]           a replacement
    ["create", "delete"]           a replacement with create_before_destroy

Any action list containing "delete" is a finding, so replacements are caught
whichever order Terraform chooses. No cloud calls, no state writes, no
network: it only reads the plan JSON.

Exit codes: 0 clean, 1 destructive change found, 2 usage or parse error.

Usage:
    terraform plan -out=tfplan
    terraform show -json tfplan | python3 tf_plan_gate.py -
    terraform show -json tfplan > plan.json && python3 tf_plan_gate.py plan.json
    python3 tf_plan_gate.py plan.json --allow 'aws_autoscaling_group.*'
    python3 tf_plan_gate.py plan.json --json

CI step, before apply:
    terraform plan -out=tfplan
    terraform show -json tfplan > plan.json
    python3 tf_plan_gate.py plan.json || exit 1

With no argument the plan is read from stdin, so a pipe is enough.

By s0sta.com
"""
import argparse
import fnmatch
import json
import sys


class PlanError(Exception):
    """Anything that should end the run with exit code 2."""


def load_plan(path):
    """Read the plan JSON from a file, or '-' for stdin."""
    if path == "-":
        try:
            return json.load(sys.stdin)
        except ValueError as exc:
            raise PlanError("stdin is not JSON: %s" % exc)
    try:
        with open(path) as handle:
            return json.load(handle)
    except OSError as exc:
        raise PlanError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise PlanError("%s is not JSON: %s" % (path, exc))


def changes_of(doc):
    """Return the resource_changes list, or fail when this is not a plan."""
    if not isinstance(doc, dict):
        raise PlanError("top level is not a JSON object")
    if "resource_changes" in doc:
        return doc.get("resource_changes") or []
    if "values" in doc and "planned_values" not in doc:
        raise PlanError("this looks like a state file; pass `terraform show -json <planfile>`")
    if "planned_values" not in doc and "format_version" not in doc:
        raise PlanError("no resource_changes; is this `terraform show -json` output?")
    return []


def collect(changes, allow):
    """Split resource changes into (findings, allowed) on destructive actions."""
    findings, allowed = [], []
    for change in changes:
        if not isinstance(change, dict):
            raise PlanError("resource_changes contains something that is not an object")
        address = change.get("address") or "(no address)"
        detail = change.get("change")
        if not isinstance(detail, dict):
            raise PlanError("%s has no change object" % address)
        actions = detail.get("actions") or []
        if not isinstance(actions, list):
            raise PlanError("%s has a non-list actions field" % address)
        if "delete" not in actions:
            continue
        kind = "replace" if "create" in actions else "delete"
        record = {"address": address, "kind": kind, "actions": actions}
        if any(fnmatch.fnmatch(address, pattern) for pattern in allow):
            allowed.append(record)
        else:
            findings.append(record)
    return findings, allowed


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Fail when a Terraform plan deletes or replaces resources.",
        epilog="Exit codes: 0 clean, 1 destructive change, 2 usage or parse error.")
    parser.add_argument("plan", nargs="?", default="-",
                        help="plan JSON from terraform show -json, default - (stdin)")
    parser.add_argument("--allow", action="append", default=[], metavar="PATTERN",
                        help="exempt addresses matching a shell wildcard, repeatable")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON report instead of text")
    args = parser.parse_args(argv)

    try:
        doc = load_plan(args.plan)
        changes = changes_of(doc)
        findings, allowed = collect(changes, args.allow)
    except PlanError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    deletes = [f for f in findings if f["kind"] == "delete"]
    replaces = [f for f in findings if f["kind"] == "replace"]

    if args.json:
        report = {
            "ok": not findings,
            "resource_changes": len(changes),
            "findings": findings,
            "allowed": allowed,
            "deletes": len(deletes),
            "replaces": len(replaces),
        }
        print(json.dumps(report, indent=None if args.quiet else 2, sort_keys=True))
    else:
        if not args.quiet:
            for item in findings:
                print("%-7s %s  %s" % (item["kind"].upper(), item["address"],
                                       ",".join(item["actions"])))
            for item in allowed:
                print("allow   %s  %s" % (item["address"], ",".join(item["actions"])))
        if findings:
            print("ALERT %d destructive: %d delete, %d replace"
                  % (len(findings), len(deletes), len(replaces)))
        else:
            print("OK no deletes or replaces in %d resource changes" % len(changes))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
