#!/usr/bin/env python3
"""Scan git history for secrets that were committed and later removed.

Usage:
    python3 git_secret_history.py
    python3 git_secret_history.py --repo /srv/app
    python3 git_secret_history.py --patch /tmp/change.patch

How it works:
    Runs "git log -p --all --no-color" (or reads a patch file), tracks the
    current commit and file, and scans only added lines for:
      - AWS access key IDs (AKIA, ASIA and the other IAM prefixes)
      - PEM private key blocks
      - bearer tokens of 20 characters or more
    Matched values are never printed; the commit, the file and the rule are.

Exit codes:
    0  no secrets found
    1  at least one secret found
    2  usage or input error

Run it in CI on every pull request, or weekly from cron:

    0 3 * * 0 python3 /opt/s0sta/git_secret_history.py --repo /srv/app

By s0sta.com
"""
import argparse
import os
import re
import subprocess
import sys

RULES = (
    ("aws-access-key",
     re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA|ANPA|ANVA|ASCA)[0-9A-Z]{16}\b")),
    ("private-key",
     re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY(?: BLOCK)?-----")),
    ("bearer-token",
     re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE)),
)
COMMIT_RE = re.compile(r"^commit ([0-9a-f]{7,40})\b")
FROM_RE = re.compile(r"^From ([0-9a-f]{7,40}) ")
FILE_RE = re.compile(r"^\+\+\+ b/(.+?)\s*$")


def scan(text, source):
    """Yield (commit, path, rule) for every added line that matches a rule."""
    commit, path = source, "?"
    for line in text.splitlines():
        match = COMMIT_RE.match(line) or FROM_RE.match(line)
        if match:
            commit = match.group(1)
            continue
        match = FILE_RE.match(line)
        if match:
            path = match.group(1)
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for name, pattern in RULES:
            if pattern.search(line):
                yield commit, path, name


def read_git(repo):
    cmd = ["git", "-C", repo, "--no-pager", "log", "-p", "--all", "--no-color"]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
    except OSError as exc:
        print("cannot run git: {}".format(exc), file=sys.stderr)
        return None
    if proc.returncode != 0:
        message = proc.stderr.strip() or "git log failed"
        print(message, file=sys.stderr)
        return None
    return proc.stdout


def main():
    ap = argparse.ArgumentParser(
        description="Scan git history for AWS keys, private key blocks and "
                    "bearer tokens.")
    ap.add_argument("--repo", default=".",
                    help="git repository to scan (default: .)")
    ap.add_argument("--patch", metavar="FILE",
                    help="read a patch file instead of running git log")
    args = ap.parse_args()

    if args.patch:
        if not os.path.isfile(args.patch):
            ap.error("no such patch file: {}".format(args.patch))
        try:
            with open(args.patch, "r", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            ap.error("cannot read {}: {}".format(args.patch, exc.strerror))
        source = "patch"
    else:
        if not os.path.isdir(args.repo):
            ap.error("not a directory: {}".format(args.repo))
        text = read_git(args.repo)
        if text is None:
            return 2
        source = "worktree"

    found = list(scan(text, source))
    for commit, path, name in found:
        print("{:<12}  {:<40}  {}".format(commit[:12], path, name))
    if found:
        print("{} secret(s) in history".format(len(found)))
        return 1
    print("clean: no secrets in the scanned history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
