---
id: p446
title: "A config linter in Python"
slug: a-config-linter-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [DevOps, Python, Security, Configuration, CICD]
source: "LinkedIn post P446 · DevOps series"
linkedin_date: 2029-08-02
design: code
script: config_lint.py
---

# A config linter in Python

A production .env file is a small document with a large blast radius. Four mistakes account for most of the incidents it causes, and they are cheap to catch before a deploy.

## Quick reference

The full script is at the end of this note: `config_lint.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 config_lint.py .env.prod --require DATABASE_URL
```

**Example output**

```text
DUP 1 EMPTY 1
MISSING 1 SECRET 1
```

## Explained

### Four checks

Duplicate keys. The same key appears twice, and the last one wins silently. The value someone read at the top of the file is not the value the process gets.

Empty values. A key exists but its value is empty after quotes are stripped. It passes a presence check and fails at the first request.

Missing required keys. The file never defines DATABASE_URL, or defines a near miss like DATABASE_URLS. The process starts and dies on the first connection.

Plaintext secrets. A secret-looking key holds a production-looking value: not a placeholder, not an interpolation. If it is committed, assume it is leaked and rotate it before you remove it; Git remembers history.

### The run

Run `python3 config_lint.py .env.prod --require DATABASE_URL`. The editor shows the condensed checker: it splits each KEY=VALUE line and builds four lists: duplicates, empty values, missing required keys, and secret keys with values over seven characters. The two output lines give the counts, and the exit code is 1 when any list is non-empty.

The attached script adds line numbers, JSON duplicate detection, placeholder rules and a per-finding report.

> **The honest caveat:** a secret that looks real may be a dead test key, and a strong production key may look ordinary. The linter finds commits, not live credentials; rotate first, then clean.

> **The lesson:** a config file is code, so lint it like code.

## In one line

> **Declared is not the same as live.** A linter reads what is written; a diff reads what runs.

**Lint before deploy**

```bash
python3 config_lint.py .env.prod
```

## Script: config_lint.py

Download: [scripts/config_lint.py](../scripts/config_lint.py)

```python
#!/usr/bin/env python3
"""config_lint.py - lint .env files and JSON config for common mistakes.

Four checks, per file:

    duplicate  the same key defined more than once
    empty      a key whose value is empty
    missing    a key named by --require that is not defined
    secret     a secret-looking key committed with a real value in plaintext

Usage:
    python3 config_lint.py .env
    python3 config_lint.py .env.prod config.json --require DATABASE_URL
    python3 config_lint.py config/*.json --require API_KEY --require REGION
    python3 config_lint.py --help

The .env reader takes KEY=VALUE lines, skips blank lines and # comments, allows
an export prefix, and strips one layer of matching quotes. The JSON reader
takes a flat or nested object, reports nested keys in dotted form, and detects
duplicate keys with object_pairs_hook because json.load keeps only the last.

Exit codes: 0 clean, 1 findings, 2 usage or input error.
Read-only: every file is opened for reading and nothing is written.

Placeholders are not findings: changeme, ${VAR}, <your-key>, ***, example,
none, null, todo and anything starting with your- or replace- are ignored.

CI:   python3 config_lint.py .env.prod --require DATABASE_URL --require API_KEY
Cron: 30 7 * * 1 python3 /opt/s0sta/config_lint.py /srv/app/.env.prod --require DATABASE_URL

By s0sta.com
"""
import argparse
import json
import re
import sys
from pathlib import Path

SECRET_KEY = re.compile(
    r"(SECRET|TOKEN|PASSWORD|PASSWD|API_KEY|ACCESS_KEY|PRIVATE|CREDENTIAL"
    r"|(^|_)(KEY|PASS)(_|$))",
    re.I,
)

TOKEN_SHAPE = re.compile(
    r"(AKIA[0-9A-Z]{16}"
    r"|sk_live_[0-9A-Za-z]{8,}"
    r"|ghp_[0-9A-Za-z]{20,}"
    r"|github_pat_[0-9A-Za-z_]{20,}"
    r"|xox[baprs]-[0-9A-Za-z-]{10,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|://[^/\s:@]+:[^/\s@]+@)"
)

PLACEHOLDERS = {"***", "changeme", "change-me", "example", "none", "null",
                "todo", "xxx"}
PLACEHOLDER_PREFIXES = ("${", "<", "your-", "replace-")


class InputError(Exception):
    """A file that cannot be read or does not parse."""


def is_placeholder(value):
    """True for an empty or obviously fake value."""
    text = value.strip().lower()
    return (not text or text in PLACEHOLDERS
            or text.startswith(PLACEHOLDER_PREFIXES))


def looks_secret(key, value):
    """True when a key and value look like a plaintext secret."""
    text = str(value).strip()
    if is_placeholder(text) or "PUBLIC_KEY" in key.upper():
        return False
    if TOKEN_SHAPE.search(text):
        return True
    return bool(SECRET_KEY.search(key)) and len(text) >= 8


def read_text(path):
    """Read one UTF-8 file, or raise InputError."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except UnicodeDecodeError as exc:
        raise InputError("cannot decode %s: %s" % (path, exc))


def parse_env(text):
    """Return (rows, duplicates) for a .env document.

    rows is a list of (line number, key, value); duplicates is a list of
    (line number, key, first line number).
    """
    rows, duplicates, first = [], [], {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key in first:
            duplicates.append((number, key, first[key]))
        else:
            first[key] = number
        rows.append((number, key, value))
    return rows, duplicates


def flatten(obj, prefix=""):
    """Yield (dotted key, value) for a nested JSON object."""
    for key, value in obj.items():
        full = prefix + key
        if isinstance(value, dict):
            yield from flatten(value, full + ".")
        else:
            yield full, value


def parse_json(path, text):
    """Return (rows, duplicate keys) for a JSON object."""
    duplicates = []

    def hook(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                duplicates.append(key)
            obj[key] = value
        return obj

    try:
        data = json.loads(text, object_pairs_hook=hook)
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict):
        raise InputError("%s must contain a JSON object" % path)
    rows = [(None, key, value) for key, value in flatten(data)]
    return rows, sorted(set(duplicates))


def lint_file(path, required):
    """Return a list of (line number or None, message) findings."""
    text = read_text(path)
    findings = []
    if path.suffix.lower() == ".json":
        rows, duplicate_keys = parse_json(path, text)
        for key in duplicate_keys:
            findings.append((None, "duplicate key %s" % key))
    else:
        rows, duplicates = parse_env(text)
        for number, key, first in duplicates:
            findings.append((number, "duplicate key %s (first at line %d)"
                             % (key, first)))

    keys = {key for _, key, _ in rows}
    for key in required:
        if key not in keys:
            findings.append((None, "missing required key %s" % key))

    seen = set()
    for number, key, value in rows:
        if key in seen:
            continue
        seen.add(key)
        if str(value).strip() == "":
            findings.append((number, "empty value for %s" % key))
        elif looks_secret(key, value):
            findings.append((number, "plaintext secret in %s" % key))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="config_lint.py",
        description="Lint .env files and JSON config for duplicate keys, "
                    "empty values, missing required keys and plaintext "
                    "secrets.")
    parser.add_argument("files", nargs="+", type=Path, metavar="FILE",
                        help=".env or .json file to check")
    parser.add_argument("--require", action="append", default=[], metavar="KEY",
                        help="key that must exist; repeatable")
    args = parser.parse_args(argv)

    required = list(dict.fromkeys(args.require))
    total = 0
    for path in args.files:
        try:
            findings = lint_file(path, required)
        except InputError as exc:
            parser.error(str(exc))
        for number, message in findings:
            where = "%s:%d" % (path, number) if number else str(path)
            print("%s: %s" % (where, message))
        total += len(findings)

    if total:
        print("%d finding%s in %d file%s"
              % (total, "" if total == 1 else "s",
                 len(args.files), "" if len(args.files) == 1 else "s"))
        return 1
    print("OK %d file%s clean"
          % (len(args.files), "" if len(args.files) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
