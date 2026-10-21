#!/usr/bin/env python3
"""Scan a terraform.tfstate file for values that look like secrets.

    python3 terraform_state_secrets.py terraform.tfstate
    python3 terraform_state_secrets.py state.json --min-length 32

Walks every value, finds strings whose key looks like a credential
(password, secret, token, key) and long random-looking strings. Prints the
path only and replaces the value with ***. Exits 1 on findings, 0 when
clean, and 2 on a missing file, invalid JSON or a top-level that is not an
object. Read-only.

CI/cron: python3 terraform_state_secrets.py terraform.tfstate || exit 1
By s0sta.com
"""
import argparse
import json
import math
import re
import sys

KEY = re.compile(r"(?i)(password|passwd|passphrase|secret|token|key)$")
SAFE = re.compile(r"(?i)(public|map_key|foreign_key|partition_key|sort_key|"
                  r"primary_key|key_name|hash|checksum|etag|digest|fingerprint|"
                  r"uuid|_id|_arn|^id$)$")


def entropy(value):
    """Shannon entropy in bits per character."""
    counts = {}
    for char in value:
        counts[char] = counts.get(char, 0) + 1
    total = float(len(value))
    return -sum(count / total * math.log2(count / total) for count in counts.values())


def random_looking(value, min_length):
    """True for a long string with mixed character classes and high entropy."""
    if len(value) < min_length:
        return False
    classes = sum((any(c.islower() for c in value),
                   any(c.isupper() for c in value),
                   any(c.isdigit() for c in value),
                   any(not c.isalnum() for c in value)))
    return classes >= 3 and entropy(value) >= 3.5


def walk(value, path="$"):
    """Yield (path, string) for every string in the JSON tree."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, "%s.%s" % (path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, "%s.%s" % (path, index))
    elif isinstance(value, str):
        yield path, value


def main(argv=None):
    """Scan the state file and return the process exit code."""
    parser = argparse.ArgumentParser(
        description="Find secret-looking values in a Terraform state file.")
    parser.add_argument("state", help="terraform.tfstate or any state JSON")
    parser.add_argument("--min-length", type=int, default=24,
                        help="shortest random-looking string to report (default: 24)")
    args = parser.parse_args(argv)
    if args.min_length < 8:
        parser.error("--min-length must be at least 8")
    try:
        with open(args.state, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        print("ERROR cannot read %s: %s" % (args.state, exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print("ERROR invalid JSON in %s: %s" % (args.state, exc), file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("ERROR %s: top level must be a JSON object" % args.state,
              file=sys.stderr)
        return 2

    findings = []
    for path, value in walk(data):
        leaf = path.rsplit(".", 1)[-1]
        if not value or SAFE.search(leaf):
            continue
        if KEY.search(leaf) or random_looking(value, args.min_length):
            findings.append(path)
    findings.sort()
    if not findings:
        print("OK no secret-looking values")
        return 0
    for path in findings:
        print("FINDING %s ***" % path)
    return 1


if __name__ == "__main__":
    sys.exit(main())
