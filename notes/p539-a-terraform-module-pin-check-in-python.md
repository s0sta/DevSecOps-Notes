---
id: p539
title: "A Terraform module pin check in Python"
slug: a-terraform-module-pin-check-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Terraform, SupplyChain, DevSecOps, Python, IaC]
source: "LinkedIn post P539 · PythonSec series"
linkedin_date: 2030-03-07
design: code
script: tf_module_pins.py
---

# A Terraform module pin check in Python

A module block with a source and no version is a dependency that updates itself. The next terraform init can pull a different tree, and the plan will not show why.

## Quick reference

The full script is at the end of this note: `tf_module_pins.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 tf_module_pins.py infra/
```

**Example output**

```text
UNPINNED infra/main.tf vpc version
UNPINNED infra/main.tf app ref
```

## Explained

### What it reads

The script walks a directory for .tf files and finds every module block. It reads the source and the version, then applies two rules. A registry source needs a version constraint. A git source needs a ref that is a full commit SHA, not a branch or a tag. Local paths are skipped; the attached script adds a third rule for other remote sources that carry neither.

### Why the SHA

A branch is a pointer. The commit it names today is not the commit it names next week, so the module you reviewed is not the module that runs. A tag is better but still movable. A 40-character SHA names one tree, so a plan is reproducible and an upgrade becomes a visible diff.

### The output

Each finding prints the file, the module name and a reason: version or ref. `python3 tf_module_pins.py infra/` prints UNPINNED infra/main.tf vpc version when the registry module has no constraint, then exits 1. A clean tree exits 0.

> **The honest caveat:** this is a text scan, not an HCL parser. Module blocks produced by Terragrunt or a template, or files generated at plan time, can be missed, so run it beside terraform validate, not instead of it.

> **The lesson:** every module source is a dependency, and every dependency needs a pin.

## In one line

> **A module is a dependency too.** It runs with your credentials, in your account.

**Check one module**

```bash
python3 tf_module_pins.py .
```

## Script: tf_module_pins.py

Download: [scripts/tf_module_pins.py](../scripts/tf_module_pins.py)

```python
#!/usr/bin/env python3
"""Check that every Terraform module source is pinned.

    python3 tf_module_pins.py infra/
    python3 tf_module_pins.py . --quiet

Walks a directory for .tf files and reads every module block. A registry
module (namespace/name/provider) needs a version constraint; a git module
needs a ref that is a full commit SHA; any other remote source needs a
version or a SHA ref. Local paths are skipped. Exits 1 when a module is
unpinned, 0 when every module is pinned, and 2 on a missing directory or an
unreadable file. Read-only.

CI/cron: python3 tf_module_pins.py infra/ || exit 1
By s0sta.com
"""
import argparse
import os
import re
import sys

MODULE = re.compile(r'\bmodule\s+"([A-Za-z0-9_-]+)"\s*\{')
SOURCE = re.compile(r'\bsource\s*=\s*"([^"]*)"')
VERSION = re.compile(r'\bversion\s*=\s*"([^"]*)"')
REGISTRY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"[?&]ref=([0-9a-fA-F]{40}|[0-9a-fA-F]{64})(?:[&#]|$)")


def clean(text):
    """Blank comments and heredocs but keep strings, so braces still match."""
    out, index, size = [], 0, len(text)
    while index < size:
        char = text[index]
        if char == "<" and text.startswith("<<", index):
            match = re.match(r"<<-?([A-Za-z_][A-Za-z0-9_]*)", text[index:])
            if match:
                token = re.escape(match.group(1))
                start = index + match.end()
                closing = re.compile(r"(?m)^[ \t]*%s[ \t]*$" % token).search(text, start)
                end = closing.end() if closing else size
                out.append("\n" * text.count("\n", index, end))
                index = end
                continue
        if char == '"':
            out.append(char)
            index += 1
            while index < size:
                out.append(text[index])
                if text[index] == "\\" and index + 1 < size:
                    out.append(text[index + 1])
                    index += 2
                    continue
                if text[index] == '"':
                    index += 1
                    break
                index += 1
            continue
        if char == "#" or (char == "/" and index + 1 < size and text[index + 1] == "/"):
            while index < size and text[index] != "\n":
                out.append(" ")
                index += 1
            continue
        if char == "/" and index + 1 < size and text[index + 1] == "*":
            out.append("  ")
            index += 2
            while index < size and not (text[index] == "*" and index + 1 < size
                                        and text[index + 1] == "/"):
                out.append("\n" if text[index] == "\n" else " ")
                index += 1
            if index < size:
                out.append("  ")
                index += 2
            continue
        out.append(char)
        index += 1
    return "".join(out)


def close_brace(text, start):
    """Return the index of the brace closing the block opened at start."""
    depth, index, quoted = 0, start, False
    while index < len(text):
        char = text[index]
        if quoted:
            if char == "\\":
                index += 2
                continue
            if char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return -1


def blocks(path):
    """Yield (module name, line, body) for each module block in one file."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = clean(handle.read())
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    for match in MODULE.finditer(text):
        start = match.end() - 1
        end = close_brace(text, start)
        if end < 0:
            raise ValueError("%s: module %s has no closing brace"
                             % (path, match.group(1)))
        line = text.count("\n", 0, match.start()) + 1
        yield match.group(1), line, text[start + 1:end]


def is_git(source):
    """True for the git source forms Terraform accepts."""
    return (source.startswith(("git::", "git@", "github.com/", "bitbucket.org/"))
            or ".git" in source)


def pin_reason(source, body):
    """Return the reason a module is unpinned, or None when it is pinned."""
    if not source or source.startswith(("./", "../", "/")):
        return None
    version = VERSION.search(body)
    has_version = bool(version and version.group(1).strip())
    ref = SHA.search(source)
    if REGISTRY.match(source):
        return None if has_version else "version"
    if is_git(source):
        if not ref:
            return "ref"
        return None
    if not has_version and not ref:
        return "source"
    return None


def main(argv=None):
    """Scan the directory and return the process exit code."""
    parser = argparse.ArgumentParser(
        description="Find Terraform modules without a pin.")
    parser.add_argument("path", nargs="?", default=".",
                        help="directory to scan (default: .)")
    args = parser.parse_args(argv)
    if not os.path.isdir(args.path):
        print("ERROR not a directory: %s" % args.path, file=sys.stderr)
        return 2

    findings, files = [], 0
    for root, dirs, names in os.walk(args.path):
        dirs[:] = sorted(name for name in dirs if name not in (".git", ".terraform"))
        for name in sorted(names):
            if not name.endswith(".tf"):
                continue
            files += 1
            path = os.path.join(root, name)
            try:
                for module, line, body in blocks(path):
                    source = SOURCE.search(body)
                    source = source.group(1) if source else ""
                    reason = pin_reason(source, body)
                    if reason:
                        findings.append((path, line, module, reason))
            except ValueError as exc:
                print("ERROR %s" % exc, file=sys.stderr)
                return 2

    if not files:
        print("OK no .tf files under %s" % args.path)
        return 0
    findings.sort()
    for path, _line, module, reason in findings:
        print("UNPINNED %s %s %s" % (path, module, reason))
    if not findings:
        print("OK every module source is pinned")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
