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
