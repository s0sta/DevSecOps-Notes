#!/usr/bin/env python3
"""Scan a CI log for likely secrets without printing the secret.

Reads one log file (or stdin), checks each line against the shapes that leak
most often in build output, and prints one masked line per hit:

    LEAK 12 aws-access-key ****************
    LEAK 40 bearer ****************

The value is never printed, not even a prefix: a short prefix is still a
secret. The line number and the kind are enough to find the line and rotate
the credential.

Patterns: AWS access key IDs (AKIA/ASIA), AWS secret access keys, GitHub and
GitLab tokens, Slack tokens, private key headers, Bearer tokens and generic
api_key/secret/token/password assignments. The match is only the trigger; the
line text is discarded.

Usage:
    python3 ci_log_leak.py build.log
    cat build.log | python3 ci_log_leak.py
    gh run view 123456 --log > /tmp/run.log
    python3 ci_log_leak.py /tmp/run.log

Exit codes: 0 no likely secret, 1 at least one finding, 2 usage or an
unreadable input.

CI (scan a saved job log before it is uploaded):
    python3 ci_log_leak.py build.log || exit 1

Cron (scan yesterday's deploy log):
    15 5 * * * python3 /opt/s0sta/ci_log_leak.py /var/log/deploy.log

The scan is read-only and opens no network socket. It is pattern matching,
not proof: a secret split across lines, base64-encoded, or written by a tool
in another format is missed. GitHub and GitLab mask exact values in the live
log, but a transformed value or a debug dump can still print. Revoke first,
then remove the line; deleting the log does not un-leak the credential.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import re
import sys

MASK = "*" * 16

PATTERNS = (
    ("aws-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("aws-secret-key", re.compile(
        r"(?i)aws_?secret_?access_?key\s*[:=]\s*[\"']?[A-Za-z0-9/+=]{40}")),
    ("private-key", re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY(?: BLOCK)?-----")),
    ("github-token", re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,})\b")),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*")),
    ("assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*"
        r"[\"']?[A-Za-z0-9_\-./+=]{12,}")),
)


def scan_line(line):
    """Return the kind of the first matching pattern, or None."""
    for kind, pattern in PATTERNS:
        if pattern.search(line):
            return kind
    return None


def read_lines(source):
    """Return the lines of a log file or stdin, or raise OSError."""
    if source == "-":
        return sys.stdin.readlines()
    with open(source, "r", encoding="utf-8", errors="replace") as handle:
        return handle.readlines()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Find likely secrets in a CI log and print the line "
                    "number with a masked value, never the value.",
        epilog="Exit codes: 0 clean, 1 findings, 2 usage or input error.")
    parser.add_argument("log", nargs="?", default="-",
                        help="log file, or - for stdin (default)")
    args = parser.parse_args(argv)

    try:
        lines = read_lines(args.log)
    except (OSError, UnicodeError) as exc:
        print("ERR cannot read %s: %s" % (args.log, exc), file=sys.stderr)
        return 2

    hits = []
    for number, line in enumerate(lines, 1):
        kind = scan_line(line)
        if kind is not None:
            hits.append((number, kind))
    if not hits:
        print("OK no likely secrets in %d lines" % len(lines))
        return 0
    print("SCAN %d lines, %d findings" % (len(lines), len(hits)))
    for number, kind in hits:
        print("LEAK %d %s %s" % (number, kind, MASK))
    return 1


if __name__ == "__main__":
    sys.exit(main())
