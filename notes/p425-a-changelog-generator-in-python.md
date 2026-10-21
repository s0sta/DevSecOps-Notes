---
id: p425
title: "A changelog generator in Python"
slug: a-changelog-generator-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Git, Python, ReleaseEngineering, CICD, DevOps]
source: "LinkedIn post P425 · DevOps series"
linkedin_date: 2029-06-14
design: code
script: changelog.py
---

# A changelog generator in Python

Release notes are usually written from memory at six on a Friday, which is why they read like a receipt. The commit subjects already contain the raw material, if the team writes conventional commits.

## Quick reference

The full script is at the end of this note: `changelog.py` (standard library only, no `pip install`).

**Run it**

```bash
git log --pretty=format:'%s' | python3 changelog.py
```

**Example output**

```text
## Unreleased
- **feat**: add SSO login
```

## Explained

### What it does

The script reads the output of `git log --pretty=format:'%s'`, one subject per line. It matches the conventional form: a type, an optional scope, an optional exclamation mark for a breaking change, then a colon and the description. It keeps feat, fix, docs, refactor, perf and test, groups the subjects by type, and prints a markdown list under ## Unreleased. If nothing matches, it prints an error and exits 1.

### Why subjects

A subject is short, stable and already reviewed, because it travelled through the pull request. The type is the only taxonomy a first draft needs. Grouping by type puts the features above the chores, and the breaking marker tells the reader what to check before upgrading.

### How to use it

`git log --pretty=format:'%s' v1.3.0..v1.4.0 | python3 changelog.py` -. Run it in the release job, write the output to `CHANGELOG.md`, and edit the paragraphs by hand. Exit 0 means a changelog was written, 1 means there were no conventional commits, 2 means the input could not be read.

> **The honest caveat:** a generated changelog records what changed, not why it matters, and a squash merge can hide twenty commits behind one vague subject.

> **The lesson:** generate the list, then write the story.

## In one line

> **Subjects are not release notes.** Group the commits, then write the why by hand.

**Read the range**

```bash
git log --oneline v1.3.0..v1.4.0
```

## Script: changelog.py

Download: [scripts/changelog.py](../scripts/changelog.py)

```python
#!/usr/bin/env python3
"""Build release notes from conventional commit subjects.

Reads the output of:

    git log --pretty=format:'%s' v1.3.0..v1.4.0

one subject per line, keeps the conventional types below, groups them by
type and prints markdown. Lines that are not conventional commits are
ignored, which is why a merge commit does not break the run.

Usage:
    git log --pretty=format:'%s' v1.3.0..v1.4.0 | python3 changelog.py -
    python3 changelog.py commits.txt --version v1.4.0

CI: run the first command as a step in the release job and redirect
stdout to CHANGELOG.md. Read-only: this script writes no files.

Exit codes: 0 changelog written, 1 no conventional commits, 2 usage or
input error.

By s0sta.com
"""
import argparse
import re
import sys

# Order is the order of the sections in the output.
SECTIONS = (
    ("feat", "Features"),
    ("fix", "Bug fixes"),
    ("docs", "Documentation"),
    ("refactor", "Refactoring"),
    ("perf", "Performance"),
    ("test", "Tests"),
)
KINDS = {kind for kind, _ in SECTIONS}
SUBJECT = re.compile(
    r"^(?P<kind>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<text>.+)$"
)


def parse(line):
    """Return (kind, scope, breaking, text) for a kept subject, else None."""
    match = SUBJECT.match(line.strip())
    if not match:
        return None
    kind = match.group("kind")
    if kind not in KINDS:
        return None
    breaking = bool(match.group("bang")) or "BREAKING CHANGE" in line
    return kind, match.group("scope"), breaking, match.group("text")


def read_lines(path):
    """Read the subject list from a file, or from stdin when path is '-'."""
    if path == "-":
        return sys.stdin.read().splitlines()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().splitlines()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Group conventional commit subjects into release notes."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="file of commit subjects, one per line (default: stdin)",
    )
    parser.add_argument(
        "--version",
        default="Unreleased",
        metavar="LABEL",
        help="heading after '##' (default: Unreleased)",
    )
    args = parser.parse_args(argv)

    try:
        lines = read_lines(args.input)
    except OSError as exc:
        print("ERR cannot read input: %s" % exc, file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("ERR input is not UTF-8 text", file=sys.stderr)
        return 2

    groups = {kind: [] for kind in KINDS}
    total = 0
    for line in lines:
        parsed = parse(line)
        if parsed is None:
            continue
        kind, scope, breaking, text = parsed
        entry = "- " + text
        if scope:
            entry += " (%s)" % scope
        if breaking:
            entry = "- **BREAKING** " + text
            if scope:
                entry += " (%s)" % scope
        groups[kind].append(entry)
        total += 1

    if total == 0:
        print("ERR no conventional commits in input", file=sys.stderr)
        return 1

    print("## %s" % args.version)
    for kind, heading in SECTIONS:
        entries = groups[kind]
        if not entries:
            continue
        print("")
        print("### %s" % heading)
        for entry in entries:
            print(entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
