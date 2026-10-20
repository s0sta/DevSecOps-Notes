---
id: p254
title: "An IAM wildcard scanner in Python"
slug: an-iam-wildcard-scanner-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [AWS, IAM, CloudSecurity, Python, DevSecOps]
source: "LinkedIn post P254 · Platform series"
linkedin_date: 2028-05-11
design: code
script: iam_wildcard.py
---

# An IAM wildcard scanner in Python

An IAM policy can grant every action on every resource in one line. Most teams find out during a review, or after an incident. This script reads the policy JSON and fails on the wildcards.

## Quick reference

The full script is at the end of this note: **iam_wildcard.py** (standard library only, no `pip install`).

**Run it**

```bash
python3 iam_wildcard.py policies/
```

**Example output**

```text
ALERT 3 wildcard grants
```

## Explained

### What it does

It walks a folder of policy documents and reads every statement. It flags an Action of "\*", an action ending in ":\*" such as s3:\* or iam:\*, and a Resource of "\*". Deny statements are skipped, because a wildcard deny restricts rather than grants. Each hit prints the file, the statement number and the value, then exits 1 so CI stops.

### Why those three

"Action": "\*" grants every action; paired with "Resource": "\*" that is full administrator, unless a Condition narrows it. "s3:\*" is every S3 call in the service, including DeleteBucket and PutBucketPolicy. "Resource": "\*" turns a narrow action into an account-wide one: s3:GetObject on \* reads every bucket you own.

### How to use it

Point it at a folder, a single file or stdin: `python3 iam_wildcard.py policies/`. In CI, run it before terraform plan and let a non-zero exit block the merge. The scan is read-only; it never calls AWS.

> **The honest caveat:** a wildcard is not automatically wrong. Some AWS actions only work with "Resource": "\*", and a tightly conditioned wildcard can be defensible. The script shows you where to look; a human still decides.

> **The lesson:** least privilege is not a policy you write once. It is a check that runs on every change.

## In one line

> **A wildcard is a permission you forgot.** Every \* is a grant someone will eventually find.

**List local policies**

```bash
aws iam list-policies --scope Local
```

## Script: iam_wildcard.py

Download: [scripts/iam_wildcard.py](../scripts/iam_wildcard.py)

```python
#!/usr/bin/env python3
"""iam_wildcard.py - find wildcard grants in AWS IAM policy JSON.

Reads IAM policy documents and flags the three patterns that quietly widen
permissions:

    "Action": "*"        every action
    "Action": "s3:*"     every action in one service
    "Resource": "*"      every resource the action can touch

Statements with "Effect": "Deny" are skipped, because a wildcard in a Deny
restricts access instead of granting it. NotAction and NotResource are out of
scope. The tool is read-only: it never calls AWS and never edits a policy.

Usage:
    python3 iam_wildcard.py policies/
    python3 iam_wildcard.py policy.json
    cat policy.json | python3 iam_wildcard.py -

Exit codes: 0 clean, 1 wildcard grant found, 2 usage or read error.

CI:
    python3 iam_wildcard.py infra/policies || exit 1
Cron (weekly, Monday 06:00):
    0 6 * * 1 python3 iam_wildcard.py /srv/policies >> /var/log/iam-wildcard.log 2>&1

By s0sta.com
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import unquote

ENVELOPES = ("Document", "PolicyDocument", "AssumeRolePolicyDocument")


def unwrap(doc):
    """Return the policy document inside common API envelopes."""
    if not isinstance(doc, dict):
        return doc
    if "Statement" in doc:
        return doc
    for key in ENVELOPES:
        inner = doc.get(key)
        if isinstance(inner, str):
            try:
                inner = json.loads(unquote(inner))
            except (ValueError, TypeError):
                continue
        if isinstance(inner, dict) and "Statement" in inner:
            return inner
    version = doc.get("PolicyVersion")
    if isinstance(version, dict):
        inner = version.get("Document")
        if isinstance(inner, str):
            try:
                inner = json.loads(unquote(inner))
            except (ValueError, TypeError):
                return doc
        if isinstance(inner, dict) and "Statement" in inner:
            return inner
    return doc


def statements(doc):
    """Yield (number, statement) for each statement in the document."""
    doc = unwrap(doc)
    if not isinstance(doc, dict):
        return
    body = doc.get("Statement")
    if isinstance(body, dict):
        body = [body]
    if not isinstance(body, list):
        return
    for i, st in enumerate(body, 1):
        if isinstance(st, dict):
            yield i, st


def as_list(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return []


def scan(doc):
    """Return a list of (statement number, kind, value, condition keys)."""
    hits = []
    for i, st in statements(doc):
        effect = str(st.get("Effect", "?"))
        if effect.lower() == "deny":
            continue
        cond = st.get("Condition")
        cond_keys = ", ".join(sorted(cond)) if isinstance(cond, dict) else ""
        for action in as_list(st.get("Action")):
            if action in ("*", "*:*"):
                hits.append((i, "Action", action, "every action", cond_keys))
            elif action.endswith(":*") and action.count(":") == 1:
                service = action.split(":", 1)[0]
                hits.append((i, "Action", action, "every action in " + service, cond_keys))
        for resource in as_list(st.get("Resource")):
            if resource == "*":
                hits.append((i, "Resource", resource, "every resource", cond_keys))
    return hits


def candidates(paths, recursive):
    """Return (files, errors); stdin is represented by None."""
    files, errors = [], []
    for raw in paths:
        if raw == "-":
            files.append(None)
            continue
        path = Path(raw)
        if path.is_dir():
            found = path.rglob("*.json") if recursive else path.glob("*.json")
            batch = sorted(p for p in found if p.is_file())
            if not batch:
                errors.append("no .json files under %s" % path)
            files.extend(batch)
        elif path.is_file():
            files.append(path)
        else:
            errors.append("not found: %s" % path)
    return files, errors


def load(path):
    if path is None:
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Flag wildcard actions and resources in AWS IAM policy JSON.")
    ap.add_argument("paths", nargs="+", metavar="PATH",
                    help="policy .json file, a directory, or - for stdin")
    ap.add_argument("--no-recursive", action="store_true",
                    help="scan only the top level of a directory")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="print the summary only")
    args = ap.parse_args(argv)

    files, errors = candidates(args.paths, not args.no_recursive)
    checked = 0
    total = 0
    hit_files = set()
    for path in files:
        label = "<stdin>" if path is None else str(path)
        try:
            doc = load(path)
        except (OSError, ValueError) as exc:
            errors.append("%s: %s" % (label, exc))
            continue
        checked += 1
        hits = scan(doc)
        if hits:
            hit_files.add(label)
        total += len(hits)
        if hits and not args.quiet:
            for num, kind, value, note, cond in hits:
                extra = "  [condition: %s]" % cond if cond else ""
                print("[WILDCARD] %s:statement %d  %s=\"%s\"  (%s)%s"
                      % (label, num, kind, value, note, extra))
    for err in errors:
        print("error: %s" % err, file=sys.stderr)
    print("%d file(s) checked, %d wildcard grant(s) in %d file(s)"
          % (checked, total, len(hit_files)))
    if total:
        print("ALERT %d wildcard grant%s" % (total, "" if total == 1 else "s"))
    if errors:
        return 2
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
```
