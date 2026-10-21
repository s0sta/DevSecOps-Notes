---
id: p445
title: "An environment diff in Python"
slug: an-environment-diff-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Python, DevOps, Configuration, CICD, SRE]
source: "LinkedIn post P445 · DevOps series"
linkedin_date: 2029-07-31
design: code
script: env_diff.py
---

# An environment diff in Python

Staging has a key production does not, and nobody can say which one is right. Two JSON manifests and one Python script settle it in a second.

## Quick reference

The full script is at the end of this note: `env_diff.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 env_diff.py staging.json prod.json
```

**Example output**

```text
MISSING API_KEY ***
MISSING 2 EXTRA 1 CHANGED 2
```

## Explained

### The code

The editor shows a short script. First the imports and a regex that matches secret-looking names: SECRET, TOKEN, KEY, PASS. The m function returns three stars for those keys and truncates every other value to forty characters, so the report fits a terminal. Then it loads both manifests from the command line and builds three sorted lists: keys missing from the target, keys only in the target, and keys present in both with different values. Three loops print each list, a summary prints the counts, and the exit call returns 1 if any list is non-empty.

### The run

`python3 env_diff.py staging.json prod.json` compares the two files. The output starts with a masked MISSING line and ends with the counts: two missing, one extra and two changed. Nothing leaves the machine and nothing is written.

### How to use it

Export each environment to a flat JSON object, keep the files beside the chart, and run the diff in CI before a deploy. Exit 0 means the manifests agree, 1 means they differ, 2 means a file is missing or not valid JSON.

> **The honest caveat:** the diff compares declared values, not the running process. A variable injected at boot or overridden on one host will not appear; compare printenv dumps when the question is what is live.

> **The lesson:** a readable diff is the cheapest review an environment gets.

## In one line

> **Parity is a diff you can read.** Run it before a deploy, not after the outage.

**Run it in ci**

```bash
python3 env_diff.py a.json b.json
```

## Script: env_diff.py

Download: [scripts/env_diff.py](../scripts/env_diff.py)

```python
#!/usr/bin/env python3
"""env_diff.py - compare two environment manifests and report the differences.

Each manifest is a flat JSON object that maps a configuration key to a value.
The script reports keys missing from the second manifest, keys that exist only
in the second, and keys whose value changed. Values under secret-looking keys
are masked, so the report is safe to paste into a ticket or a CI log.

Usage:
    python3 env_diff.py base.json target.json
    python3 env_diff.py staging.json production.json
    python3 env_diff.py --help

Exit codes: 0 no differences, 1 differences found, 2 usage or input error.
Read-only: both files are opened for reading and nothing is written.

CI:   python3 env_diff.py staging.json prod.json || echo "environments differ"
Cron: 0 6 * * * python3 /opt/s0sta/env_diff.py /srv/app/staging.json /srv/app/prod.json

By s0sta.com
"""
import argparse
import json
import re
import sys

SECRET_KEY = re.compile(
    r"(SECRET|TOKEN|PASSWORD|PASSWD|API_KEY|ACCESS_KEY|PRIVATE|CREDENTIAL"
    r"|(^|_)(KEY|PASS)(_|$))",
    re.I,
)

URL_CREDS = re.compile(r"(://[^/\s:@]+:)[^/\s@]+@")


class InputError(Exception):
    """A manifest that cannot be read or does not look like an object."""


def load_manifest(path):
    """Read one flat JSON object and return it as a dict."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict):
        raise InputError("%s must contain a JSON object" % path)
    return data


def display(key, value):
    """Return a printable value, masked when the key or URL looks secret."""
    if SECRET_KEY.search(key):
        return "***"
    text = URL_CREDS.sub(r"\1***@", str(value))
    return text if len(text) <= 40 else text[:37] + "..."


def compare(base, target):
    """Return (missing, extra, changed), all sorted."""
    missing = sorted(set(base) - set(target))
    extra = sorted(set(target) - set(base))
    changed = sorted(
        k for k in set(base) & set(target) if base[k] != target[k])
    return missing, extra, changed


def report(base, target, missing, extra, changed):
    """Print the three sections and the summary line."""
    for key in missing:
        print("MISSING %s = %s" % (key, display(key, base[key])))
    for key in extra:
        print("EXTRA %s = %s" % (key, display(key, target[key])))
    for key in changed:
        print("CHANGED %s: %s -> %s"
              % (key, display(key, base[key]), display(key, target[key])))
    print("%d missing, %d extra, %d changed"
          % (len(missing), len(extra), len(changed)))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="env_diff.py",
        description="Compare two JSON environment manifests and report keys "
                    "that are missing, extra or changed. Secret-looking "
                    "values are masked.")
    parser.add_argument("base", help="baseline manifest, a JSON object")
    parser.add_argument("target",
                        help="manifest to compare against the baseline")
    args = parser.parse_args(argv)

    try:
        base = load_manifest(args.base)
        target = load_manifest(args.target)
    except InputError as exc:
        parser.error(str(exc))

    missing, extra, changed = compare(base, target)
    report(base, target, missing, extra, changed)
    return 1 if (missing or extra or changed) else 0


if __name__ == "__main__":
    sys.exit(main())
```
