---
id: p397
title: "A Terraform security audit in Python"
slug: a-terraform-security-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Terraform, DevSecOps, IaC, Python, CloudNative]
source: "LinkedIn post P397 · DevSecOps series"
linkedin_date: 2029-04-10
design: code
script: iac_audit.py
---

# A Terraform security audit in Python

A Terraform file can describe a public bucket, an open port and a wildcard policy in twenty lines. This audit reads the HCL for five of those smells and fails the build.

## Quick reference

The full script is at the end of this note: `iac_audit.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 iac_audit.py infra/
```

**Example output**

```text
ALERT main.tf 14 acl
ALERT main.tf 22 ingress
```

## Explained

### What it checks

Five patterns. A public S3 ACL: acl = "public-read" or "public-read-write", which makes the bucket readable without a signed request. An open ingress: cidr_blocks with 0.0.0.0/0 or ::/0, which lets the internet reach the security group. An unencrypted volume: encrypted = false, also the default when the attribute is absent. A wildcard IAM action: Action = "\*" or actions = ["\*"]. A hard-coded secret: password or secret assigned to a literal string instead of a variable.

### Why regex on HCL

The standard library has no HCL parser, and these five are single-line facts. The script reads one .tf file at a time, matches each line, and reports the file, line and rule. It ignores quoted values that start with a dollar sign, so an interpolated reference is not a finding.

### How to use it

`python3 iac_audit.py infra/` scans a directory recursively and exits 1 on a match. Run it before terraform plan, then let the plan review cover what a line scan cannot. Exit 2 means the path was missing or held no .tf files.

> **The honest caveat:** an omitted encrypted attribute is not caught by a line scan, and account-level EBS encryption may already cover the volume the file leaves unset. The finding is a question, not a verdict.

> **The lesson:** catch the obvious misconfiguration in review, and let the plan catch the rest.

## In one line

> **Read the source before the plan.** The scanner sees intent; the plan sees the account.

**Scan the source**

```bash
trivy config .
```

## Script: iac_audit.py

Download: [scripts/iac_audit.py](../scripts/iac_audit.py)

```python
#!/usr/bin/env python3
"""Audit Terraform HCL for five common security smells.

Each .tf file is read as text and checked for:

  * a public S3 ACL (public-read or public-read-write)
  * an ingress rule open to 0.0.0.0/0 or ::/0
  * an EBS volume with encrypted = false
  * an IAM policy with a wildcard action
  * a hard-coded password, secret, key or token

Usage:
    python3 iac_audit.py infra/
    python3 iac_audit.py infra/ main.tf
    python3 iac_audit.py . --quiet

Exit codes:
    0  no findings
    1  at least one finding
    2  usage error, or a path that is missing, unreadable, or holds no
       .tf files

A directory is scanned recursively for .tf files. The audit is read-only:
files are opened for reading and nothing is written.
It is line-based, so it does not follow values across lines or modules; use
terraform plan and a policy engine for the rest.

Cron: 30 6 * * 1 python3 iac_audit.py infra/
CI:   python3 iac_audit.py infra/

By s0sta.com
"""

import argparse
import os
import re
import sys

RULES = [
    ("public-acl",
     re.compile(r'\bacl\s*=\s*"public-read(-write)?"')),
    ("open-ingress",
     re.compile(r'(?:ipv6_)?cidr_blocks\s*=\s*\[[^\]]*"'
                r'(?:0\.0\.0\.0/0|::/0)"')),
    ("unencrypted-volume",
     re.compile(r'\bencrypted\s*=\s*(?:false|"false")')),
    ("wildcard-iam",
     re.compile(r'"?(?:[Aa]ctions?)"?\s*[:=]\s*(?:"\*"|\[[^\]]*"\*")')),
    ("hardcoded-secret",
     re.compile(r'\b(?:password|secret|secret_key|access_key|api_key|token)'
                r'\s*=\s*"[^"$][^"]*"')),
]

KINDS = {name: name.replace("-", " ") for name, _ in RULES}


class AuditError(Exception):
    """The input cannot be audited."""


def terraform_files(paths):
    """Return a sorted list of .tf files from files and directories."""
    found = []
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, names in os.walk(path):
                dirs[:] = sorted(d for d in dirs if d != ".git")
                for name in sorted(names):
                    if name.endswith(".tf"):
                        found.append(os.path.join(root, name))
        elif os.path.isfile(path):
            found.append(path)
        else:
            raise AuditError("no such file or directory: %s" % path)
    if not found:
        raise AuditError("no .tf files found in %s" % ", ".join(paths))
    return sorted(set(found))


def audit_file(path):
    """Return the findings for one .tf file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError as exc:
        raise AuditError("cannot read %s: %s" % (path, exc))

    findings = []
    for number, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        for name, pattern in RULES:
            if pattern.search(line):
                findings.append((path, number, name))
    return findings


def audit(paths):
    """Audit every file and return (files, findings)."""
    files = terraform_files(paths)
    findings = []
    for path in files:
        findings.extend(audit_file(path))
    findings.sort(key=lambda item: (item[0], item[1], item[2]))
    return files, findings


def plural(count, word):
    """Return a count and a correctly pluralised noun."""
    return "%d %s%s" % (count, word, "" if count == 1 else "s")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit Terraform HCL for five common security smells.",
        epilog="Exit 0 clean, 1 finding, 2 usage or input error. By s0sta.com")
    parser.add_argument("paths", nargs="*", default=["."],
                        help=".tf files or directories (default: .)")
    parser.add_argument("--quiet", action="store_true",
                        help="print only the summary line")
    args = parser.parse_args(argv)

    try:
        files, findings = audit(args.paths or ["."])
    except AuditError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    if not args.quiet:
        for path, number, name in findings:
            print("ALERT %s:%d %s" % (path, number, name))
        for name in sorted({name for _, _, name in findings}):
            print("NOTE  %s" % KINDS[name])

    if findings:
        print("FAIL %s in %s" % (plural(len(findings), "finding"),
                                 plural(len(files), "file")))
        return 1
    print("OK %s checked" % plural(len(files), "file"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
