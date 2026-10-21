#!/usr/bin/env python3
"""log_redact.py - redact secrets and identifiers from log lines.

Reads log text from files or stdin, masks email addresses, IPv4 addresses,
bearer tokens and long hexadecimal strings, and writes the result to stdout.
The input files are never modified.

    EMAIL    [EMAIL]        anything shaped like user@example.com
    IPv4     [IP]           10.0.0.7, 192.168.1.20
    TOKEN    Bearer [TOKEN] the credential after a Bearer scheme
    HEX      [HEX]          32 or more hexadecimal characters

Usage:
    python3 log_redact.py app.log
    cat app.log | python3 log_redact.py
    journalctl -u api --since -1h | python3 log_redact.py > safe.log
    python3 log_redact.py access.log error.log
    python3 log_redact.py --help

CI (sanitise an artefact before upload):
    python3 log_redact.py build.log > build.redacted.log || exit 2

Cron (a daily archive of one service log):
    15 2 * * * journalctl -u api --since -1d | python3 /opt/s0sta/log_redact.py >> /var/log/api.redacted

Exit codes: 0 input read and redacted, 2 usage or unreadable input.
A redaction is the job, not a failure, so a file with hits still exits 0.

Read-only: it writes nothing except stdout and opens no network socket.

The patterns are deliberately narrow. They catch the common shapes and miss
secrets split across lines, encoded blobs and credentials in other formats.
A redacted log is safer, not safe.

By s0sta.com
"""
import argparse
import re
import sys

PATTERNS = (
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP]"),
    (re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/-]+=*"), r"\1[TOKEN]"),
    (re.compile(r"\b[0-9A-Fa-f]{32,}\b"), "[HEX]"),
)


def redact(line):
    """Return one line with every known shape replaced."""
    for pattern, replacement in PATTERNS:
        line = pattern.sub(replacement, line)
    return line


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Redact emails, IPv4 addresses, bearer tokens and long "
                    "hex strings from log lines.")
    parser.add_argument("files", nargs="*", metavar="FILE",
                        help="log files; read stdin when none is given")
    args = parser.parse_args(argv)
    for name in args.files or ["-"]:
        try:
            if name == "-":
                for line in sys.stdin:
                    sys.stdout.write(redact(line))
            else:
                with open(name, "r", encoding="utf-8") as handle:
                    for line in handle:
                        sys.stdout.write(redact(line))
        except (OSError, UnicodeError) as exc:
            print("log_redact: %s: %s" % (name, exc), file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
