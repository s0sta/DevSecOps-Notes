---
id: p396
title: "A GitHub Actions audit in Python"
slug: a-github-actions-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, DevSecOps, CICD, GitHubActions, SupplyChain]
source: "LinkedIn post P396 · DevSecOps series"
linkedin_date: 2029-04-08
design: code
script: gha_audit.py
---

# A GitHub Actions audit in Python

Every workflow file in the repository is a small program with a token attached. This audit reads them as text, because the standard library has no YAML parser and the checks do not need one.

## Quick reference

The full script is at the end of this note: `gha_audit.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 gha_audit.py .github/workflows
```

**Example output**

```text
ALERT ci.yml 12
ALERT ci.yml 40
```

## Explained

### What it checks

Five things, in order. A file with no permissions: block is counted once, because the repository default then decides what the token can do. Then each line is read and four checks can add a finding: pull_request_target, write-all, a secrets. reference inside a run block, tracked by indentation so the block's later lines count, and a uses: reference whose ref is not a 40-character SHA.

### Why line by line

PyYAML is not in the standard library, and adding a dependency to an audit tool defeats the point. Workflow YAML is regular enough for these checks: keys sit on their own lines, run blocks are indented, and uses values are single tokens. The full script skips local actions and docker:// references, which have no SHA to pin.

### How to use it

`python3 gha_audit.py .github/workflows` prints one line per finding and exits 1 if there are any. Put it in a job before the build, or run it from cron against every repository. Exit 0 means clean, 2 means a path was missing or unreadable.

> **The honest caveat:** a line scan cannot evaluate expressions, anchors or reusable workflows, and a risky key inside a quoted string will still be flagged. Read the findings; do not just count them.

> **The lesson:** a workflow is code, so review it like code and pin what it calls.

## In one line

> **A workflow is code.** The runner trusts it. Audit it like code.

**Run it in ci**

```bash
python3 gha_audit.py .github/workflows
```

## Script: gha_audit.py

Download: [scripts/gha_audit.py](../scripts/gha_audit.py)

```python
#!/usr/bin/env python3
"""Audit GitHub Actions workflows for five common configuration risks.

Each workflow is read as text and checked for:

  * a file that never sets permissions:
  * the pull_request_target event
  * permissions: write-all
  * a secrets expression inside a run: block
  * a uses: reference pinned to a tag or branch, not a full commit SHA

Usage:
    python3 gha_audit.py .github/workflows
    python3 gha_audit.py .github/workflows ci.yml
    python3 gha_audit.py . --quiet

Exit codes:
    0  no findings
    1  at least one finding
    2  usage error, or a path that is missing, unreadable, or holds no
       workflow files

A directory is scanned recursively for .yml and .yaml files. The audit is
read-only: files are opened for reading and nothing is written.
It is deliberately line-based, so it cannot evaluate expressions, aliases or
reusable workflows; treat a finding as a line to review, not a verdict.

Cron: 0 7 * * 1 python3 gha_audit.py .github/workflows
CI:   python3 gha_audit.py .github/workflows

By s0sta.com
"""

import argparse
import os
import re
import sys

EXTENSIONS = (".yml", ".yaml")
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
RUN_RE = re.compile(r"^(\s*)(?:-\s+)?run:")
USES_RE = re.compile(r"^\s*(?:-\s+)?uses:\s*(\S+)")
SECRET_EXPR_RE = re.compile(r"\$\{\{[^}]*\bsecrets\.")

KINDS = {
    "permissions-missing": "permissions: is not set, so the repository default applies",
    "pull_request_target": "pull_request_target runs with the base repository's trust",
    "write-all": "permissions: write-all grants every scope",
    "secrets-in-run": "a secrets expression is used inside a run: block",
    "unpinned-action": "an action is pinned to a tag or branch, not a commit SHA",
}


class AuditError(Exception):
    """The input cannot be audited."""


def workflow_files(paths):
    """Return a sorted list of workflow files from files and directories."""
    found = []
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, names in os.walk(path):
                dirs[:] = sorted(d for d in dirs if d != ".git")
                for name in sorted(names):
                    if name.endswith(EXTENSIONS):
                        found.append(os.path.join(root, name))
        elif os.path.isfile(path):
            found.append(path)
        else:
            raise AuditError("no such file or directory: %s" % path)
    if not found:
        raise AuditError("no workflow files found in %s" % ", ".join(paths))
    return sorted(set(found))


def read_lines(path):
    """Read a workflow file and return its lines, or raise AuditError."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read().splitlines()
    except OSError as exc:
        raise AuditError("cannot read %s: %s" % (path, exc))


def code_part(line):
    """Return the line with a trailing comment removed (best effort)."""
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return ""
    quote = None
    for index, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "#" and index and line[index - 1] in " \t":
            return line[:index]
    return line


def check_uses(line, number, path, findings):
    """Report a uses: reference that is not pinned to a 40-character SHA."""
    match = USES_RE.match(line)
    if not match:
        return
    value = match.group(1).strip().strip("'\"")
    if value.startswith(("./", "docker://")) or "@" not in value:
        return
    ref = value.rsplit("@", 1)[1]
    if not SHA_RE.match(ref):
        findings.append((path, number, "unpinned-action"))


def audit_file(path):
    """Return the findings for one workflow file."""
    lines = read_lines(path)
    findings = []
    code = [code_part(line) for line in lines]

    if not any("permissions:" in line for line in code):
        findings.append((path, 0, "permissions-missing"))

    run_indent = None
    for number, line in enumerate(lines, 1):
        text = code[number - 1]
        if "pull_request_target" in text:
            findings.append((path, number, "pull_request_target"))
        if "write-all" in text:
            findings.append((path, number, "write-all"))
        check_uses(text, number, path, findings)

        match = RUN_RE.match(text)
        if match:
            run_indent = text.index("run:")
            inline = text[match.end():]
            if SECRET_EXPR_RE.search(inline):
                findings.append((path, number, "secrets-in-run"))
            continue

        if run_indent is None:
            continue
        if not text.strip():
            continue
        indent = len(text) - len(text.lstrip())
        if indent > run_indent:
            if SECRET_EXPR_RE.search(text):
                findings.append((path, number, "secrets-in-run"))
        else:
            run_indent = None

    return findings


def audit(paths):
    """Audit every workflow and return (files, findings)."""
    files = workflow_files(paths)
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
        description="Audit GitHub Actions workflows for five configuration risks.",
        epilog="Exit 0 clean, 1 finding, 2 usage or input error. By s0sta.com")
    parser.add_argument("paths", nargs="*", default=["."],
                        help="workflow files or directories (default: .)")
    parser.add_argument("--quiet", action="store_true",
                        help="print only the summary line")
    args = parser.parse_args(argv)

    try:
        files, findings = audit(args.paths or ["."])
    except AuditError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2

    if not args.quiet:
        for path, number, kind in findings:
            print("ALERT %s:%d %s" % (path, number, kind))
        for kind in sorted({kind for _, _, kind in findings}):
            print("NOTE  %s" % KINDS[kind])

    if findings:
        print("FAIL %s in %s" % (plural(len(findings), "finding"),
                                 plural(len(files), "file")))
        return 1
    print("OK %s checked" % plural(len(files), "workflow"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
