---
id: p546
title: "An S3 bucket config audit in Python"
slug: an-s3-bucket-config-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [AWS, S3, CloudSecurity, Python, DevSecOps]
source: "LinkedIn post P546 · PythonSec series"
linkedin_date: 2030-03-24
design: code
script: s3_config_audit.py
---

# An S3 bucket config audit in Python

The bucket has a policy, the policy looks narrow, and the review stops there. Encryption is off, versioning is suspended, logging is disabled and the ACL still grants AllUsers read.

## Quick reference

The full script is at the end of this note: `s3_config_audit.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 s3_config_audit.py /tmp/bucket.json
```

**Example output**

```text
ALERT enc log
```

## Explained

### Five settings

Encryption: a default rule must exist, not just a KMS key somewhere in the account. Versioning: Status must be Enabled, because Suspended is not a backup. Public access block: all four flags must be true. Logging: LoggingEnabled needs a TargetBucket. ACL: no grant may go to AllUsers or AuthenticatedUsers.

### The frame

The condensed version builds a dictionary of five booleans, collects the failed keys and prints them. On the fixture it prints ALERT enc log and exits 1: encryption and logging are the two missing sections. The attached script prints one FAIL line per finding and the same exit code.

### How to run it

Collect the five API responses, join them with `jq -s` into one file, then run `python3 s3_config_audit.py /tmp/bucket.json`. In CI, run it on a saved bundle; from cron, on a nightly export. Exit 0 is clean, 1 is a finding, 2 is a usage or input error.

> **The honest caveat:** the audit reads configuration, not the objects. A bucket can be encrypted and still hold public data, and a missing section is treated as a finding rather than a pass.

> **The lesson:** a bucket is safe when five settings agree, not when one policy looks narrow.

## In one line

> **A bucket is five settings.** Public is a state, not a checkbox you ticked once.

**Audit one bucket**

```bash
python3 s3_config_audit.py /tmp/b.json
```

## Script: s3_config_audit.py

Download: [scripts/s3_config_audit.py](../scripts/s3_config_audit.py)

```python
#!/usr/bin/env python3
"""Audit one S3 bucket configuration and flag missing or public settings.

Reads a JSON bundle with the five settings that decide whether a bucket is
safe by default:

    encryption             aws s3api get-bucket-encryption
    versioning             aws s3api get-bucket-versioning
    public_access_block    aws s3api get-public-access-block
    logging                aws s3api get-bucket-logging
    acl                    aws s3api get-bucket-acl

The bundle is one object with those keys, for example:

    {
      "bucket": "demo",
      "encryption": {"ServerSideEncryptionConfiguration": {"Rules": [...]}},
      "versioning": {"Status": "Enabled"},
      "public_access_block": {"PublicAccessBlockConfiguration": {...}},
      "logging": {"LoggingEnabled": {"TargetBucket": "logs", ...}},
      "acl": {"Grants": [...]}
    }

Build it from the API responses (encryption and the public access block
return an error when they are not configured, so keep an empty object):

    aws s3api get-bucket-encryption --bucket demo > /tmp/enc.json 2>/dev/null \
        || echo '{}' > /tmp/enc.json
    aws s3api get-bucket-versioning --bucket demo > /tmp/ver.json
    aws s3api get-public-access-block --bucket demo > /tmp/pab.json 2>/dev/null \
        || echo '{}' > /tmp/pab.json
    aws s3api get-bucket-logging --bucket demo > /tmp/log.json
    aws s3api get-bucket-acl --bucket demo > /tmp/acl.json
    jq -s '{encryption:.[0], versioning:.[1], public_access_block:.[2],
            logging:.[3], acl:.[4]}' /tmp/enc.json /tmp/ver.json \
        /tmp/pab.json /tmp/log.json /tmp/acl.json > /tmp/bucket.json

The script checks:
    encryption           a default encryption rule must exist
    versioning           Status must be Enabled
    public access block  all four block settings must be true
    logging              LoggingEnabled with a TargetBucket must exist
    acl                  no grant to AllUsers or AuthenticatedUsers

Usage:
    python3 s3_config_audit.py /tmp/bucket.json
    cat /tmp/bucket.json | python3 s3_config_audit.py -
    python3 s3_config_audit.py /tmp/bucket.json --quiet

Exit codes: 0 clean, 1 at least one finding, 2 usage or unreadable/invalid
input. A missing section is a finding, not a pass: absent configuration is
what the audit exists to catch.

CI (a non-zero exit fails the job):
    python3 s3_config_audit.py /tmp/bucket.json || exit 1
Cron (daily at 06:20):
    20 6 * * * python3 /opt/s0sta/s3_config_audit.py /srv/s3/bucket.json

Read-only: opens one local file (or stdin) and writes nothing.
Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys

PAB_KEYS = ("BlockPublicAcls", "IgnorePublicAcls",
            "BlockPublicPolicy", "RestrictPublicBuckets")
PUBLIC_GROUP_SUFFIXES = ("/AllUsers", "/AuthenticatedUsers")


class AuditError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source):
    """Read the bundle from a file or '-' for stdin."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise AuditError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise AuditError("%s is not JSON: %s" % (source, exc))


def section(doc, *names):
    """Return a named section, or an empty object when it is absent."""
    for name in names:
        if name in doc:
            value = doc[name]
            if value is None:
                return {}
            if not isinstance(value, dict):
                raise AuditError("%s must be a JSON object" % name)
            return value
    return {}


def check_encryption(doc):
    """A default server-side encryption rule must exist."""
    sec = section(doc, "encryption", "Encryption")
    config = sec.get("ServerSideEncryptionConfiguration")
    if config is None:
        return ["encryption: no ServerSideEncryptionConfiguration"]
    if not isinstance(config, dict):
        raise AuditError("encryption ServerSideEncryptionConfiguration must be an object")
    rules = config.get("Rules")
    if not isinstance(rules, list) or not rules:
        return ["encryption: no default encryption rule"]
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        default = rule.get("ApplyServerSideEncryptionByDefault")
        if isinstance(default, dict) and default.get("SSEAlgorithm"):
            return []
    return ["encryption: rule has no SSEAlgorithm"]


def check_versioning(doc):
    """Versioning must be Enabled, not Suspended or absent."""
    sec = section(doc, "versioning", "Versioning")
    status = sec.get("Status")
    if status == "Enabled":
        return []
    return ["versioning: %s" % (status or "missing")]


def check_public_access_block(doc):
    """All four account-level block settings must be true."""
    sec = section(doc, "public_access_block", "publicAccessBlock",
                  "PublicAccessBlock", "public-access-block")
    config = sec.get("PublicAccessBlockConfiguration")
    if config is None:
        return ["public access block: missing"]
    if not isinstance(config, dict):
        raise AuditError("PublicAccessBlockConfiguration must be an object")
    findings = []
    for key in PAB_KEYS:
        if config.get(key) is not True:
            findings.append("public access block: %s=%s"
                            % (key, config.get(key)))
    return findings


def check_logging(doc):
    """Server access logging must have a destination bucket."""
    sec = section(doc, "logging", "Logging")
    enabled = sec.get("LoggingEnabled")
    if enabled is None:
        return ["logging: access logging disabled"]
    if not isinstance(enabled, dict):
        raise AuditError("LoggingEnabled must be an object")
    if not enabled.get("TargetBucket"):
        return ["logging: no TargetBucket"]
    return []


def check_acl(doc):
    """No grant may go to AllUsers or AuthenticatedUsers."""
    sec = section(doc, "acl", "Acl", "ACL")
    grants = sec.get("Grants")
    if grants is None:
        return ["acl: no Grants list to inspect"]
    if not isinstance(grants, list):
        raise AuditError("acl Grants must be a list")
    findings = []
    for grant in grants:
        if not isinstance(grant, dict):
            raise AuditError("every acl Grant must be an object")
        grantee = grant.get("Grantee")
        uri = ""
        if isinstance(grantee, dict):
            uri = grantee.get("URI") or ""
        if isinstance(uri, str) and uri.endswith(PUBLIC_GROUP_SUFFIXES):
            group = uri.rsplit("/", 1)[-1]
            findings.append("acl: %s %s" % (grant.get("Permission", "?"), group))
    return findings


CHECKS = (
    ("encryption", check_encryption),
    ("versioning", check_versioning),
    ("public access block", check_public_access_block),
    ("logging", check_logging),
    ("acl", check_acl),
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit an S3 bucket config bundle: encryption, versioning, "
                    "public access block, logging and ACL.",
        epilog="Exit codes: 0 clean, 1 findings, 2 usage or input error.")
    parser.add_argument("config", nargs="?", default="-",
                        help="bucket config JSON file, or - for stdin (default: -)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args(argv)

    try:
        doc = read_json(args.config)
        if not isinstance(doc, dict):
            raise AuditError("the config must be a JSON object")
        present = ("encryption", "Encryption", "versioning", "Versioning",
                   "public_access_block", "publicAccessBlock", "PublicAccessBlock",
                   "public-access-block", "logging", "Logging", "acl", "Acl", "ACL")
        if not any(key in doc for key in present):
            raise AuditError("no S3 config sections found; expected encryption, "
                             "versioning, public_access_block, logging and acl")
        findings = []
        for _name, check in CHECKS:
            findings.extend(check(doc))
    except AuditError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    bucket = doc.get("bucket")
    if not args.quiet:
        for finding in findings:
            print("FAIL " + finding)

    if findings:
        where = " for %s" % bucket if isinstance(bucket, str) and bucket else ""
        print("ALERT %d finding%s%s" % (len(findings),
                                        "" if len(findings) == 1 else "s", where))
        return 1
    print("OK all five S3 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
