#!/usr/bin/env python3
"""Flag public, anonymously listable and unencrypted storage buckets.

Usage:
    python3 bucket_exposure.py inventory.csv
    python3 bucket_exposure.py inventory.json --max 20

Input (an export, never a cloud API call):
    JSON: [{"provider": "aws", "bucket": "acme-logs", "acl": "private",
            "public_access_block": true, "policy": "...", "encryption": "AES256"}]
          or {"buckets": [...]}
    CSV:  provider,bucket,acl,public_access_block,policy,encryption

Providers: aws (s3), gcp (gcs), azure (blob). public_access_block true means
the account-level public-access prevention control is on, so a legacy public
grant is reported as blocked rather than exposed.

Scores are the sum of the flags, printed with the factors:
    public 40, anon-list 30, no-enc 20.

Cron/CI:
    0 7 * * 1 python3 bucket_exposure.py /srv/exports/storage.csv

Exit codes:
    0 no exposure
    1 at least one exposed bucket
    2 bad input (unreadable file, bad JSON/CSV, unknown provider, bad boolean)

Read-only: it makes no network calls and writes nothing. By s0sta.com
"""
import argparse
import csv
import io
import json
import re
import sys

WEIGHT = {"public": 40, "anon-list": 30, "no-enc": 20}
PROVIDERS = {
    "aws": ("aws", "s3", "amazon"),
    "gcp": ("gcp", "gcs", "gs", "google"),
    "azure": ("azure", "az", "blob", "microsoft"),
}
PUBLIC_PRINCIPAL = re.compile(r'"principal"\s*:\s*"\*"')
PUBLIC_PRINCIPAL_OBJECT = re.compile(r'"principal"\s*:\s*\{[^{}]*"\*"')


def fail(message):
    print("ERROR %s" % message, file=sys.stderr)
    return 2


def norm_keys(row):
    return {str(k).strip().lower(): v for k, v in row.items() if k is not None}


def as_bool(value):
    """True/False, or None when the export left the field blank."""
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if not text:
        return None
    if text in ("true", "1", "yes", "on", "enabled", "enforce", "enforced"):
        return True
    if text in ("false", "0", "no", "off", "disabled", "unblocked"):
        return False
    raise ValueError("not a boolean: %r" % str(value))


def as_provider(value):
    text = str(value or "").strip().lower()
    for canonical, aliases in PROVIDERS.items():
        if text in aliases:
            return canonical
    raise ValueError("unknown provider: %r" % text)


def encrypted(value):
    text = str(value or "").strip().lower()
    return text not in ("", "none", "false", "off", "no", "unencrypted", "-")


def policy_text(value):
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value or "")


def load(path):
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
            for key in ("buckets", "storage", "items"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
            else:
                raise ValueError("JSON object has no buckets list")
        if not isinstance(data, list):
            raise ValueError("JSON must be a list or an object with a buckets list")
        rows = []
        for i, row in enumerate(data, 1):
            if not isinstance(row, dict):
                raise ValueError("bucket %d is not an object" % i)
            rows.append(normalise(norm_keys(row), i))
        return rows

    reader = csv.DictReader(io.StringIO(raw))
    fields = [str(f).strip().lower() for f in (reader.fieldnames or [])]
    if "provider" not in fields or "bucket" not in fields:
        raise ValueError("CSV needs provider and bucket columns, got %s" % fields)
    return [normalise(norm_keys(row), i + 2) for i, row in enumerate(reader)]


def normalise(row, line_no):
    name = str(row.get("bucket") or "").strip()
    try:
        provider = as_provider(row.get("provider"))
        block = as_bool(row.get("public_access_block"))
    except ValueError as exc:
        raise ValueError("row %d (%s): %s" % (line_no, name or "?", exc))
    if not name:
        raise ValueError("row %d has no bucket" % line_no)
    return {
        "provider": provider,
        "bucket": name,
        "acl": str(row.get("acl") or "").strip().lower(),
        "block": block,
        "policy": policy_text(row.get("policy")),
        "encrypted": encrypted(row.get("encryption")),
    }


def grants(row):
    """Return (public, anonymous-list) before the account block is applied."""
    provider, acl = row["provider"], row["acl"]
    policy = row["policy"].lower()
    public = False
    listed = False

    if provider == "aws":
        if acl in ("public-read", "public-read-write"):
            public = True
            listed = True  # bucket ACL READ grants ListBucket
        elif acl == "authenticated-read":
            public = True  # any AWS account, not just this one
        if PUBLIC_PRINCIPAL.search(policy) or PUBLIC_PRINCIPAL_OBJECT.search(policy):
            public = True
            if "listbucket" in policy:
                listed = True
    elif provider == "gcp":
        anonymous = ("allusers" in policy or "allusers" in acl
                     or "public" in acl)
        if anonymous or "allauthenticatedusers" in policy:
            public = True
        if anonymous and any(token in policy for token in
                             ("objectviewer", "objectlist", "objects.list",
                              "legacyobjectreader")):
            listed = True
    else:  # azure
        if acl == "container":
            public = True
            listed = True
        elif acl == "blob":
            public = True

    if row["block"] is True:
        return False, False, public or listed
    return public, listed, False


def evaluate(row):
    public, listed, blocked = grants(row)
    flags = []
    if public:
        flags.append("public")
    if listed:
        flags.append("anon-list")
    if not row["encrypted"]:
        flags.append("no-enc")
    return flags, blocked


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Flag public, anonymously listable and unencrypted buckets.",
        epilog="Reads a multi-cloud storage inventory (JSON or CSV).")
    parser.add_argument("inventory", help="storage inventory: JSON or CSV")
    parser.add_argument("--max", type=int, default=50,
                        help="show at most N buckets (default: 50)")
    parser.add_argument("--skip-encryption", action="store_true",
                        help="do not treat a missing encryption field as a finding")
    args = parser.parse_args(argv)
    if args.max < 1:
        return fail("--max must be at least 1")

    try:
        rows = load(args.inventory)
    except ValueError as exc:
        return fail(str(exc))

    found = []
    blocked_count = 0
    for row in rows:
        flags, blocked = evaluate(row)
        if args.skip_encryption:
            flags = [flag for flag in flags if flag != "no-enc"]
        if blocked:
            blocked_count += 1
        if flags:
            total = sum(WEIGHT[flag] for flag in flags)
            found.append((total, row["bucket"], flags))
    found.sort(key=lambda item: (-item[0], item[1]))

    if not found:
        print("OK no exposed bucket in %d buckets" % len(rows))
        if blocked_count:
            print("NOTE %d public grant(s) blocked by public access prevention"
                  % blocked_count)
        return 0

    print("FINDING %d exposed buckets of %d" % (len(found), len(rows)))
    for total, name, flags in found[:args.max]:
        factors = "+".join(str(WEIGHT[flag]) for flag in flags)
        print("ALERT %d %s %s [%s]" % (total, name, ",".join(flags), factors))
    if len(found) > args.max:
        print("NOTE %d more buckets not shown" % (len(found) - args.max))
    if blocked_count:
        print("NOTE %d public grant(s) blocked by public access prevention"
              % blocked_count)
    return 1


if __name__ == "__main__":
    sys.exit(main())
