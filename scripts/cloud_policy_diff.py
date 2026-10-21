#!/usr/bin/env python3
"""Diff two IAM policy documents and report permissions that widened.

Compares an old and a new AWS IAM policy JSON document and prints:

    ADD   a statement only in the new document
    DEL   a statement only in the old document
    WIDE  a grant that became broader

A matched Allow statement is widened when its new Action or Resource list
contains a wildcard the old list did not contain, or when it adds an action
or a resource the old statement did not grant. An added Allow statement with
a wildcard, an Allow statement that was a Deny, and a removed Deny statement
also count as widening. A new Allow statement without a wildcard is printed
as ADD and passes unless --strict-adds is used.

Statements are matched by Sid. Statements without a Sid are matched by
position, so keep a Sid on every statement you review. NotAction and
NotResource are out of scope. Conditions are not evaluated: a wildcard with
a Condition is still reported as widened, so read the reason before you
fail the build.

The input can be an identity policy, a resource policy, or the output of
`aws iam get-policy-version` (the URL-encoded Document is decoded).

Usage:
    python3 cloud_policy_diff.py old.json new.json
    python3 cloud_policy_diff.py old.json new.json --quiet
    python3 cloud_policy_diff.py old.json new.json --strict-adds
    aws iam get-policy-version --policy-arn "$ARN" --version-id v7 \
        | python3 cloud_policy_diff.py /tmp/old.json -
    python3 cloud_policy_diff.py - new.json < old.json

Exit codes: 0 no widening (additions and removals still print), 1 a
permission widened, 2 usage or unreadable/invalid input.

CI (block a merge that widens):
    python3 cloud_policy_diff.py /tmp/old.json /tmp/new.json || exit 1
Cron (weekly drift check):
    0 6 * * 1 python3 /opt/s0sta/cloud_policy_diff.py /srv/iam/old.json /srv/iam/new.json

Read-only: opens the two documents and writes nothing.
Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys
from collections import Counter
from urllib.parse import unquote


class DiffError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source, label):
    """Read one JSON document from a file or '-' for stdin, then unwrap it."""
    try:
        if source == "-":
            doc = json.load(sys.stdin)
        else:
            with open(source, encoding="utf-8") as handle:
                doc = json.load(handle)
    except OSError as exc:
        raise DiffError("cannot read %s %s: %s" % (label, source, exc))
    except ValueError as exc:
        raise DiffError("%s %s is not JSON: %s" % (label, source, exc))
    return unwrap(doc, label)


def unwrap(doc, label):
    """Accept a raw policy or the usual API envelopes around one."""
    if not isinstance(doc, dict):
        raise DiffError("%s must be a JSON object" % label)
    if "Statement" in doc:
        return doc
    for field in ("Policy", "Document", "PolicyDocument", "AssumeRolePolicyDocument"):
        inner = doc.get(field)
        if isinstance(inner, str):
            try:
                inner = json.loads(unquote(inner))
            except ValueError as exc:
                raise DiffError("%s %s field is not JSON: %s" % (label, field, exc))
        if isinstance(inner, dict) and "Statement" in inner:
            return inner
    version = doc.get("PolicyVersion")
    if isinstance(version, dict):
        return unwrap(version, label)
    raise DiffError("%s has no Statement field" % label)


def statements(doc, label):
    """Return the Statement list, checking the shape as it goes."""
    body = doc.get("Statement")
    if body is None:
        return []
    if isinstance(body, dict):
        body = [body]
    if not isinstance(body, list):
        raise DiffError("%s Statement must be an object or a list" % label)
    out = []
    for number, statement in enumerate(body, 1):
        if not isinstance(statement, dict):
            raise DiffError("%s statement %d is not an object" % (label, number))
        if not isinstance(statement.get("Effect"), str):
            raise DiffError("%s statement %d has no Effect" % (label, number))
        out.append(statement)
    return out


def keyed(items):
    """Map each statement to a stable key: Sid when unique, position otherwise."""
    sids = Counter(str(st.get("Sid")) for st in items if st.get("Sid"))
    out = []
    for position, statement in enumerate(items, 1):
        sid = statement.get("Sid")
        if isinstance(sid, str) and sid and sids[sid] == 1:
            key = "sid:" + sid
        else:
            key = "pos:%d" % position
        out.append((key, statement))
    return dict(out)


def as_list(value):
    """Return a string field as a list, and drop non-string entries."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def has_wildcard(values):
    """True when any value contains a wildcard."""
    return any("*" in value for value in values)


def label_of(key):
    """Turn a matching key into something a reviewer can find in the file."""
    kind, value = key.split(":", 1)
    if kind == "sid":
        return value
    return "statement " + value


def describe(statement):
    """One compact line for an added or removed statement."""
    effect = str(statement.get("Effect", "?"))
    actions = ",".join(as_list(statement.get("Action"))) or "-"
    resources = ",".join(as_list(statement.get("Resource"))) or "-"
    if len(actions) > 42:
        actions = actions[:39] + "..."
    if len(resources) > 42:
        resources = resources[:39] + "..."
    return "%s %s on %s" % (effect, actions, resources)


def widen_reason(old, new):
    """Return a reason string when the new statement grants more than the old."""
    old_effect = str(old.get("Effect", "")).lower()
    new_effect = str(new.get("Effect", "")).lower()
    if old_effect == "deny" and new_effect == "allow":
        return "Deny became Allow"
    if new_effect != "allow":
        return None

    old_actions = as_list(old.get("Action"))
    new_actions = as_list(new.get("Action"))
    old_resources = as_list(old.get("Resource"))
    new_resources = as_list(new.get("Resource"))

    reasons = []
    wild_action = has_wildcard(new_actions) and not has_wildcard(old_actions)
    wild_resource = has_wildcard(new_resources) and not has_wildcard(old_resources)
    if wild_action:
        reasons.append("Action wildcard")
    if wild_resource:
        reasons.append("Resource wildcard")
    if not wild_action and not has_wildcard(old_actions):
        added_actions = [a for a in new_actions if a not in old_actions]
        if added_actions:
            reasons.append("new action " + ",".join(added_actions[:2]))
    if not wild_resource and not has_wildcard(old_resources):
        added_resources = [r for r in new_resources if r not in old_resources]
        if added_resources:
            reasons.append("new resource " + added_resources[0][:30])
    return "; ".join(reasons) or None


def compare(old_items, new_items, strict_adds=False):
    """Return (added, removed, widened, old_by_key, new_by_key)."""
    old = keyed(old_items)
    new = keyed(new_items)
    added = [key for key in new if key not in old]
    removed = [key for key in old if key not in new]
    widened = []

    for key in old:
        if key in new:
            reason = widen_reason(old[key], new[key])
            if reason:
                widened.append((key, reason))

    for key in added:
        statement = new[key]
        if str(statement.get("Effect", "")).lower() != "allow":
            continue
        has_star = has_wildcard(as_list(statement.get("Action")))
        has_star = has_star or has_wildcard(as_list(statement.get("Resource")))
        if has_star:
            widened.append((key, "new wildcard grant"))
        elif strict_adds:
            widened.append((key, "new Allow statement"))

    for key in removed:
        if str(old[key].get("Effect", "")).lower() == "deny":
            widened.append((key, "Deny removed"))

    return added, removed, widened, old, new


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Diff two AWS IAM policy documents and flag widened permissions.",
        epilog="Exit codes: 0 no widening, 1 widening found, 2 usage or input error.")
    parser.add_argument("old", help="old policy JSON file, or - for stdin")
    parser.add_argument("new", help="new policy JSON file, or - for stdin")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    parser.add_argument("--strict-adds", action="store_true",
                        help="treat every added Allow statement as a widening")
    args = parser.parse_args(argv)

    if args.old == "-" and args.new == "-":
        parser.error("old and new cannot both read from stdin")

    try:
        old_items = statements(read_json(args.old, "old policy"), "old policy")
        new_items = statements(read_json(args.new, "new policy"), "new policy")
        added, removed, widened, old, new = compare(old_items, new_items,
                                                    args.strict_adds)
    except DiffError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not args.quiet:
        for key in added:
            print("ADD  %s  %s" % (label_of(key), describe(new[key])))
        for key in removed:
            print("DEL  %s  %s" % (label_of(key), describe(old[key])))
        for key, reason in widened:
            print("WIDE %s  %s" % (label_of(key), reason))

    print("ADD %d DEL %d WIDE %d" % (len(added), len(removed), len(widened)))
    if widened:
        print("ALERT %d widened permission%s" % (len(widened),
                                                 "" if len(widened) == 1 else "s"))
        return 1
    print("OK no widening")
    return 0


if __name__ == "__main__":
    sys.exit(main())
