---
id: p733
title: "API keys in the JavaScript"
slug: api-keys-in-the-javascript
sections: [devsecops]
topic: "Python scripts"
tags: [AppSec, JavaScript, Python, SecretsManagement, DevSecOps]
source: "LinkedIn post P733 · ASM series"
linkedin_date: 2031-06-03
design: code
script: js_secret_scan.py
---

# API keys in the JavaScript

The bundle shipped with a live Stripe key. It worked for nine days, because the build cached it and the CDN kept serving it.

## Quick reference

The full script is at the end of this note: `js_secret_scan.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 js_secret_scan.py /tmp/js.json
```

**Example output**

```text
FINDING 5 secrets in 2 bundles
ALERT dist/app.js:1 aws AKIA...
```

## Explained

### What it does

`js_secret_scan.py` reads an export of JavaScript bundles, each with a file name and its content. It searches five patterns: AWS access key id, Google API key, Stripe live secret, bearer token and private key header. For each match it prints file:line, the pattern name and a masked value: the first four characters, never the secret. The fourteen lines print FINDING 5 secrets in 2 bundles and ALERT dist/app.js:1 aws AKIA.... The attached tool adds the value length.

### How to run it

`python3 js_secret_scan.py dist/bundles.json`. In CI, run it after the build and before the upload, and let the exit code fail the job. Exit 0 is clean, 1 is a hit, 2 is bad input. `--types` aws,stripe narrows the scan.

### The fix

Revoke the key first. Then remove it from the source, rebuild, and purge the CDN and browser caches; the old bundle is still downloadable. Moving the call server-side is the second step. Deleting the line without rotating leaves a live key in every cache.

### Prevention

Scan the built artefact, not just the repository. Add the same five patterns to pre-commit and to the upload job.

> **The honest caveat:** publishable keys are meant to ship (Stripe pk_live_, Google browser keys restricted by referrer), and this scanner only matches server-side patterns. A hit is a candidate; the owner confirms scope.

> **The lesson:** a key in a bundle is a key in every browser that loaded it.

## In one line

> **Rotate first, clean second.** Five patterns, a masked value, and an exit code a build can read.

**Scan the bundle**

```bash
python3 js_secret_scan.py dist/
```

## Script: js_secret_scan.py

Download: [scripts/js_secret_scan.py](../scripts/js_secret_scan.py)

```python
#!/usr/bin/env python3
"""Find credential patterns in exported JavaScript and print a masked hit.

Usage:
    python3 js_secret_scan.py bundles.json
    python3 js_secret_scan.py bundles.json --types aws,stripe --max 20

Input (an export, never a live fetch):
    JSON: [{"file": "dist/app.js", "content": "..."}] or {"bundles": [...]}

Patterns: AWS access key id, Google API key, Stripe live secret, bearer
token, private key header. The output is file:line, the pattern name and a
masked value: the first four characters and the length, never the secret.
A hit exits 1 so a build can fail on it.

Cron/CI:
    python3 js_secret_scan.py dist/bundles.json || exit 1

Exit codes:
    0 no match
    1 at least one match
    2 bad input (unreadable file, bad JSON, missing file/content, bad --types)

Read-only: it makes no network calls and writes nothing. By s0sta.com
"""
import argparse
import json
import re
import sys

# (name, compiled pattern, match group holding the value)
PATTERNS = [
    ("aws", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), 0),
    ("google", re.compile(r"\bAIza[0-9A-Za-z_-]{35}(?![0-9A-Za-z_-])"), 0),
    ("stripe", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{16,}\b"), 0),
    ("bearer", re.compile(r"(?i)\bbearer[ \t]+([A-Za-z0-9._~+/-]{16,}=*)"), 1),
    ("key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"), 0),
]
NAMES = tuple(name for name, _rx, _grp in PATTERNS)


def fail(message):
    print("ERROR %s" % message, file=sys.stderr)
    return 2


def mask(value):
    """Show the four-character prefix and the length only, never the value."""
    value = value.strip()
    if len(value) <= 8:
        return "*" * len(value)
    return "%s... (%d chars)" % (value[:4], len(value))


def load(path):
    """Read the bundle export and return [(file, content), ...]."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    if not raw.strip():
        raise ValueError("empty input: %s" % path)
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise ValueError("bad JSON in %s: %s" % (path, exc))

    if isinstance(data, dict):
        for key in ("bundles", "files", "items"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            raise ValueError("JSON object has no bundles list")
    if not isinstance(data, list):
        raise ValueError("JSON must be a list or an object with a bundles list")

    out = []
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            raise ValueError("bundle %d is not an object" % i)
        name = item.get("file", item.get("name", ""))
        if "content" in item:
            content = item["content"]
        elif "source" in item:
            content = item["source"]
        else:
            content = None
        if not isinstance(name, str) or not name.strip():
            raise ValueError("bundle %d has no file name" % i)
        if not isinstance(content, str):
            raise ValueError("bundle %d (%s) has no string content" % (i, name))
        out.append((name.strip(), content))
    return out


def scan(bundles, enabled):
    """Return deduplicated findings as (file, line, name, masked)."""
    hits = []
    seen = set()
    order = {name: i for i, name in enumerate(NAMES)}
    for name, content in bundles:
        for lineno, line in enumerate(content.splitlines(), 1):
            for kind, rx, group in PATTERNS:
                if kind not in enabled:
                    continue
                for match in rx.finditer(line):
                    value = match.group(group) or ""
                    key = (name, lineno, kind, value)
                    if not value or key in seen:
                        continue
                    seen.add(key)
                    hits.append((name, lineno, kind, mask(value)))
    hits.sort(key=lambda hit: (hit[0], hit[1], order[hit[2]]))
    return hits


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Find credential patterns in exported JavaScript bundles.",
        epilog="Prints file:line and a masked value. Exit 1 on any hit.")
    parser.add_argument("bundles", help="bundle export: JSON with file and content")
    parser.add_argument("--types", default=",".join(NAMES),
                        help="comma list of patterns: %s" % ", ".join(NAMES))
    parser.add_argument("--max", type=int, default=100,
                        help="show at most N hits (default: 100)")
    args = parser.parse_args(argv)

    enabled = [part.strip().lower() for part in args.types.split(",") if part.strip()]
    unknown = [part for part in enabled if part not in NAMES]
    if unknown:
        return fail("unknown type(s): %s; choose from %s"
                    % (", ".join(unknown), ", ".join(NAMES)))
    if not enabled:
        return fail("--types needs at least one pattern")
    if args.max < 1:
        return fail("--max must be at least 1")

    try:
        bundles = load(args.bundles)
    except ValueError as exc:
        return fail(str(exc))

    hits = scan(bundles, set(enabled))
    word = "bundle" if len(bundles) == 1 else "bundles"
    if not hits:
        print("OK no credential pattern in %d %s" % (len(bundles), word))
        return 0

    print("FINDING %d secrets in %d %s" % (len(hits), len(bundles), word))
    for name, lineno, kind, shown in hits[:args.max]:
        print("ALERT %s:%d %s %s" % (name, lineno, kind, shown))
    if len(hits) > args.max:
        print("NOTE %d more hits not shown" % (len(hits) - args.max))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
