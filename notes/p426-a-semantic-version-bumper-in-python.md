---
id: p426
title: "A semantic version bumper in Python"
slug: a-semantic-version-bumper-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [SemVer, Python, Git, CICD, DevOps]
source: "LinkedIn post P426 · DevOps series"
linkedin_date: 2029-06-17
design: code
script: semver_bump.py
---

# A semantic version bumper in Python

The next version number should be a decision made by the commits that caused it, not by whoever remembers to edit a file. This script reads the latest tag and the subjects since that tag, and prints the next one.

## Quick reference

The full script is at the end of this note: `semver_bump.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 semver_bump.py release.txt
```

**Example output**

```text
v1.5.0
```

## Explained

### What it does

The first line is the latest tag; every line after it is a commit subject. A subject with an exclamation mark before the colon, or the words BREAKING CHANGE, is a major change. A feat is a minor change. Every other conventional type counts as a patch. The script prints the next tag, keeping whatever v prefix the input used.

### Why classify

SemVer is a promise about compatibility. A breaking change raises the major and resets the rest; a feature raises the minor and resets the patch; a fix raises the patch. Deciding from the commits means the version cannot drift from the change that caused it, and a bot can do it in the release job while a human reviews the result.

### How to use it

`git describe --tags --abbrev=0 > /tmp/release.txt`, then `git log --no-merges --pretty=format:'%s' <tag>..HEAD >> /tmp/release.txt`, then `python3 semver_bump.py /tmp/release.txt`. Exit 0 prints the next tag, 1 lists commits it could not classify, 2 means the tag or the input is missing.

> **The honest caveat:** the script only sees the subjects. A breaking change described in a pull request body, or in a footer below the subject, will ship as a patch unless the subject carries the exclamation mark.

> **The lesson:** let the commits choose the number.

## In one line

> **The commits pick the number.** A version is a promise about compatibility, not a count of effort.

**Read the commits**

```bash
git log --pretty=format:'%s' v1.4..
```

## Script: semver_bump.py

Download: [scripts/semver_bump.py](../scripts/semver_bump.py)

```python
#!/usr/bin/env python3
"""Print the next SemVer tag from the latest tag and commit subjects.

The input is the last release tag on the first line, followed by one
commit subject per line:

    v1.4.2
    feat: add SSO login
    fix(api): correct tax rounding

A subject with '!' before the colon, or the text BREAKING CHANGE, raises
the major version. A feat raises the minor version. Every other
conventional type is a patch. Unclassified subjects stop the run.

A prerelease tag such as v1.4.2-rc.1 becomes v1.4.2 on a fix, and still
gets a minor or major bump for a feat or a breaking change.

Usage:
    git describe --tags --abbrev=0 > /tmp/release.txt
    git log --no-merges --pretty=format:'%s' v1.4.2..HEAD >> /tmp/release.txt
    python3 semver_bump.py /tmp/release.txt

CI: run it in the release job, then create and push the tag that it
prints. Read-only: this script never creates or pushes a tag.

Exit codes: 0 next tag printed, 1 unclassified commits, 2 usage or
input error.

By s0sta.com
"""
import argparse
import re
import sys

CONVENTIONAL = re.compile(
    r"^(?P<kind>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<text>.+)$"
)
TAG = re.compile(
    r"^(?P<prefix>v?)(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<pre>[0-9A-Za-z.-]+))?(?:\+(?P<build>[0-9A-Za-z.-]+))?$"
)
KINDS = {
    "feat", "fix", "docs", "style", "refactor", "perf",
    "test", "build", "ci", "chore", "revert",
}


def read_lines(path):
    """Read the tag and subjects from a file, or stdin when path is '-'."""
    if path == "-":
        return sys.stdin.read().splitlines()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().splitlines()


def classify(subject):
    """Return 'major', 'minor', 'patch' or None for one commit subject."""
    if "BREAKING CHANGE" in subject or "BREAKING-CHANGE" in subject:
        return "major"
    match = CONVENTIONAL.match(subject.strip())
    if not match:
        return None
    if match.group("kind") not in KINDS:
        return None
    if match.group("bang"):
        return "major"
    if match.group("kind") == "feat":
        return "minor"
    return "patch"


def next_version(tag, subjects):
    """Return the next tag string, or raise ValueError for a bad tag."""
    match = TAG.match(tag)
    if not match:
        raise ValueError("tag is not SemVer: %s" % tag)
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    pre = bool(match.group("pre"))

    level = 0
    unclassified = []
    for subject in subjects:
        if not subject.strip():
            continue
        kind = classify(subject)
        if kind is None:
            unclassified.append(subject.strip())
        elif kind == "major":
            level = 2
        elif kind == "minor" and level < 1:
            level = 1

    if unclassified:
        for subject in unclassified:
            print("ERR unclassified: %s" % subject, file=sys.stderr)
        print("ERR use conventional commits and filter merges with --no-merges",
              file=sys.stderr)
        return None

    if level == 2:
        major, minor, patch = major + 1, 0, 0
    elif level == 1:
        minor, patch = minor + 1, 0
    elif pre:
        pass                      # the release candidate becomes the release
    else:
        patch += 1
    return "%s%d.%d.%d" % (match.group("prefix"), major, minor, patch)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Print the next SemVer tag from commits since the last tag."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="file with the tag on line one and subjects after it (default: stdin)",
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

    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        print("ERR no tag on the first line", file=sys.stderr)
        return 2
    tag = lines[0].strip()
    subjects = lines[1:]
    if not any(subject.strip() for subject in subjects):
        print("ERR no commit subjects after the tag", file=sys.stderr)
        return 2

    try:
        tag_out = next_version(tag, subjects)
    except ValueError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2
    if tag_out is None:
        return 1
    print(tag_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
