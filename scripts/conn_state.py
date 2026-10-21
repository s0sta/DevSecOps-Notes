#!/usr/bin/env python3
"""Report TCP socket states from `ss -tan` and flag leaks or spikes.

Usage:
    ss -tan | python3 conn_state.py
    ss -tan > /tmp/ss.txt
    python3 conn_state.py --input /tmp/ss.txt
    python3 conn_state.py --input /tmp/ss.txt --close-wait 5 --time-wait 500

Reads a captured `ss -tan` table and prints a count per TCP state. It exits
1 when CLOSE-WAIT sockets reach --close-wait (default 10) or TIME-WAIT
sockets reach --time-wait (default 1000).

Exit codes: 0 clean, 1 finding, 2 usage or input error.
Read-only: parses text, prints, and never changes a socket.
Cron: * * * * * ss -tan | python3 conn_state.py >> /var/log/conn-state.log
CI:   ss -tan | python3 conn_state.py || exit 1
By s0sta.com
"""

import argparse
import collections
import sys

STATES = frozenset({
    "ESTAB", "SYN-SENT", "SYN-RECV", "FIN-WAIT-1", "FIN-WAIT-2",
    "TIME-WAIT", "CLOSE", "CLOSE-WAIT", "LAST-ACK", "LISTEN", "CLOSING",
})


def positive(text):
    """argparse type for a whole number of 1 or more."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a whole number")
    if value < 1:
        raise argparse.ArgumentTypeError("expected a number of 1 or more")
    return value


def parse(stream):
    """Return (Counter of states, number of socket rows) from ss -tan text."""
    counts = collections.Counter()
    total = 0
    for line in stream:
        fields = line.split()
        if len(fields) < 5:
            continue
        state = fields[0].upper()
        if state not in STATES:
            continue
        counts[state] += 1
        total += 1
    return counts, total


def report(counts, args):
    """Print the counts and the verdict; return 0 or 1."""
    print(f"{'total':<12}{sum(counts.values())}")
    for state, count in counts.most_common():
        print(f"{state:<12}{count}")

    findings = []
    close_wait = counts.get("CLOSE-WAIT", 0)
    time_wait = counts.get("TIME-WAIT", 0)
    if close_wait >= args.close_wait:
        findings.append(
            f"close-wait {close_wait} >= {args.close_wait}: an app is not closing sockets")
    if time_wait >= args.time_wait:
        findings.append(
            f"time-wait {time_wait} >= {args.time_wait}: short-lived connections are piling up")
    if findings:
        for finding in findings:
            print(f"FAIL {finding}")
        return 1
    print(f"OK close-wait {close_wait} < {args.close_wait}, "
          f"time-wait {time_wait} < {args.time_wait}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Count TCP states from `ss -tan` and fail on CLOSE-WAIT or TIME-WAIT.")
    parser.add_argument(
        "-i", "--input", default="-", metavar="PATH",
        help="file containing `ss -tan` output, or - for stdin (default: -)")
    parser.add_argument(
        "--close-wait", type=positive, default=10, metavar="N",
        help="fail when CLOSE-WAIT sockets reach N (default: 10)")
    parser.add_argument(
        "--time-wait", type=positive, default=1000, metavar="N",
        help="fail when TIME-WAIT sockets reach N (default: 1000)")
    args = parser.parse_args(argv)

    if args.input == "-":
        counts, total = parse(sys.stdin)
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as handle:
                counts, total = parse(handle)
        except OSError as exc:
            print(f"ERROR cannot read {args.input}: {exc}", file=sys.stderr)
            return 2

    if total == 0:
        print("ERROR no TCP states found; is this `ss -tan` output?", file=sys.stderr)
        return 2
    return report(counts, args)


if __name__ == "__main__":
    sys.exit(main())
