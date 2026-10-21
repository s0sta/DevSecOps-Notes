#!/usr/bin/env python3
"""Flag risky events in a CloudTrail JSON export.

Usage:
    python3 cloudtrail_detect.py trail.json
    python3 cloudtrail_detect.py trail.json --include-denied
    python3 cloudtrail_detect.py trail.json --json
    python3 cloudtrail_detect.py --help

Reads the Records[] array of a CloudTrail JSON export and reports four
shapes that matter:

    root console logins        ConsoleLogin with userIdentity.type == Root
    IAM policy changes         Put*, Attach*, Detach*, Delete*Policy calls
                               and policy version changes
    S3 policy changes          PutBucketPolicy, DeleteBucketPolicy,
                               PutBucketAcl, PutBucketPublicAccessBlock
    access key creation        CreateAccessKey

By default a record with an errorCode is skipped: the call was refused and
changed nothing. --include-denied reports those attempts as well.

Exit codes: 0 clean, 1 findings, 2 usage or input error.
Read-only: the trail file is opened for reading and never modified.

Cron: 15 6 * * * python3 /opt/s0sta/cloudtrail_detect.py /var/tmp/trail.json --json >> /var/log/cloudtrail.json
CI:   python3 cloudtrail_detect.py trail.json || exit 1

By s0sta.com
"""

import argparse
import json
import sys

ROOT_EVENT = "ConsoleLogin"

IAM_EVENTS = frozenset({
    "PutUserPolicy", "PutRolePolicy", "PutGroupPolicy",
    "AttachUserPolicy", "AttachRolePolicy", "AttachGroupPolicy",
    "DetachUserPolicy", "DetachRolePolicy", "DetachGroupPolicy",
    "DeleteUserPolicy", "DeleteRolePolicy", "DeleteGroupPolicy",
    "CreatePolicyVersion", "SetDefaultPolicyVersion",
    "UpdateAssumeRolePolicy",
})

S3_EVENTS = frozenset({
    "PutBucketPolicy", "DeleteBucketPolicy",
    "PutBucketAcl", "PutBucketPublicAccessBlock",
})

KEY_EVENTS = frozenset({"CreateAccessKey"})

LABELS = {
    "root": "root login",
    "iam": "iam policy",
    "s3": "s3 policy",
    "key": "access key",
}


class InputError(Exception):
    """A trail that cannot be read or does not look like CloudTrail."""


def identity_name(identity):
    """Best available name for the caller, in descending order of usefulness."""
    for key in ("arn", "userName", "principalId"):
        value = identity.get(key)
        if value:
            return str(value)
    return str(identity.get("type") or "unknown")


def classify(record):
    """Return (kind, eventName) for a record, or None if it is not a hit."""
    event = str(record.get("eventName") or "")
    identity = record.get("userIdentity")
    if not isinstance(identity, dict):
        identity = {}

    if event == ROOT_EVENT and identity.get("type") == "Root":
        return "root", event
    if event in IAM_EVENTS:
        return "iam", event
    if event in S3_EVENTS:
        return "s3", event
    if event in KEY_EVENTS:
        return "key", event
    return None


def load_records(path):
    """Read a CloudTrail export and return its records list."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))

    if isinstance(document, dict):
        records = document.get("Records")
    elif isinstance(document, list):
        records = document
    else:
        records = None

    if not isinstance(records, list):
        raise InputError("%s has no Records[] array" % path)
    return records


def scan(records, include_denied=False):
    """Return (findings, denied_skipped, records_read)."""
    findings = []
    skipped = 0
    read = 0

    for record in records:
        if not isinstance(record, dict):
            continue
        read += 1
        hit = classify(record)
        if hit is None:
            continue
        kind, event = hit
        denied = bool(record.get("errorCode"))
        if denied and not include_denied:
            skipped += 1
            continue

        identity = record.get("userIdentity")
        if not isinstance(identity, dict):
            identity = {}
        findings.append({
            "kind": LABELS[kind],
            "event": event,
            "time": str(record.get("eventTime") or ""),
            "identity": identity_name(identity),
            "source": str(record.get("sourceIPAddress") or ""),
            "region": str(record.get("awsRegion") or ""),
            "denied": denied,
            "error": str(record.get("errorCode") or ""),
        })

    return findings, skipped, read


def print_text(findings, skipped, read):
    for item in findings:
        line = "ALERT %s %s %s %s %s" % (
            item["kind"], item["time"] or "-", item["identity"],
            item["source"] or "-", item["region"] or "-")
        if item["denied"]:
            line += " DENIED " + (item["error"] or "")
        print(line)
    print("cloudtrail: %d finding%s in %d record%s (%d denied skipped)"
          % (len(findings), "" if len(findings) == 1 else "s",
             read, "" if read == 1 else "s", skipped))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="cloudtrail_detect.py",
        description="Flag root logins, IAM and S3 policy changes and new "
                    "access keys in a CloudTrail JSON export.")
    parser.add_argument("trail", help="CloudTrail JSON export (Records[] array)")
    parser.add_argument("--include-denied", action="store_true",
                        help="also report refused calls that carry an errorCode")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON object instead of text lines")
    args = parser.parse_args(argv)

    try:
        records = load_records(args.trail)
    except InputError as exc:
        parser.error(str(exc))

    findings, skipped, read = scan(records, args.include_denied)

    if args.json:
        print(json.dumps({
            "records": read,
            "findings": findings,
            "findings_count": len(findings),
            "denied_skipped": skipped,
            "clean": not findings,
        }, indent=2, sort_keys=True))
    else:
        print_text(findings, skipped, read)

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
