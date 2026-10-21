---
id: p197
title: "A secret scanner in Python for your CI"
slug: a-secret-scanner-in-python-for-your-ci
sections: [devsecops]
topic: "Python scripts"
tags: [Python, DevSecOps, CyberSecurity, CICD, Git]
source: "LinkedIn post P197 · Cloud / DevSecOps series"
linkedin_date: 2027-12-30
design: code
script: secret_scanner.py
---

# A secret scanner in Python for your CI

DevSecOps means shifting security left, catching problems before they ship. This script scans a folder for likely secrets, API keys, tokens, passwords, private keys, so you catch a leak before it reaches git, where it lives forever. Full file attached, standard library only.

## Quick reference

The full script is at the end of this note: `secret_scanner.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 secret_scanner.py .
```

**Example output**

```text
[!] config/settings.py:7  Generic API key
[FAIL] 1 potential secret(s) found
```

## Explained

### What it does

It walks the folder, reads text files, and flags lines matching patterns for common secret formats: AWS access keys, generic api_key or token assignments, Slack tokens, private key blocks. It skips binaries and folders like .git and node_modules, and exits 1 when it finds something, so it can fail a CI step or a pre-commit hook.

### Why it matters

A secret committed to git is not fixed by deleting it in the next commit; it stays in the history, and anyone with the repo can recover it. The only real fix is to rotate the key. Catching it before the push avoids all of that.

### How to use it

Locally before a commit, or as a CI step: run it, and if it exits non-zero, block the merge. `python3 secret_scanner.py .` scans the current project.

The attached version has more patterns, skips the folders and file types that cause noise, and prints the file, line number and a snippet so you can jump straight to it.

> **Honest caveat:** this is a first line of defence, not a complete solution. Dedicated tools like gitleaks or trufflehog go deeper, and a pre-commit hook plus branch protection makes it hard to bypass. But a dependency-free script you fully understand is a great place to start.

## In one line

> **Catch the leak before the push.** A key in git history is a key you must rotate.

**Add it to ci:** run it as a step; exit 1 fails the build

## Script: secret_scanner.py

Download: [scripts/secret_scanner.py](../scripts/secret_scanner.py)

```python
#!/usr/bin/env python3
"""secret_scanner.py - find leaked secrets before you commit them.

Walks a folder and flags lines that look like API keys, passwords, tokens or
private keys. Run it before a push, or in CI to block a commit. It is a
first line of defence, not a replacement for a full scanner. Stdlib only.

Usage:
    python3 secret_scanner.py .
    python3 secret_scanner.py /path/to/repo

Exit code is 1 if anything is found, so it fails a CI step.

By s0sta.com
"""
import re
import sys
from pathlib import Path

PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Generic API key": re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][0-9a-zA-Z/+_\-]{16,}['\"]"),
    "Password assignment": re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{6,}['\"]"),
    "Slack token": re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}"),
}
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".lock"}


def scan_file(path):
    hits = []
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return hits
    for i, line in enumerate(text.splitlines(), 1):
        for name, rx in PATTERNS.items():
            if rx.search(line):
                hits.append((i, name, line.strip()[:80]))
    return hits


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    found = 0
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix in SKIP_EXT:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        for lineno, name, snippet in scan_file(path):
            found += 1
            print(f"[!] {path}:{lineno}  {name}\n    {snippet}")
    print(f"\n{'[FAIL]' if found else '[OK]'} {found} potential secret(s) found")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
```
