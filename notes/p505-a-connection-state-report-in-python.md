---
id: p505
title: "A connection state report in Python"
slug: a-connection-state-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Kubernetes, Python, Networking, SRE, Linux]
source: "LinkedIn post P505 · Network series"
linkedin_date: 2029-12-18
design: code
script: conn_state.py
---

# A connection state report in Python

A pod restarts cleanly, the dashboard is green, and twenty minutes later the node cannot open new outbound connections. The socket table was filling the whole time.

## Quick reference

The full script is at the end of this note: `conn_state.py` (standard library only, no `pip install`).

**Run it**

```bash
ss -tan | python3 conn_state.py
```

**Example output**

```text
TIME-WAIT=843 CLOSE-WAIT=27 ESTAB=12
FAIL close-wait=27
```

## Explained

### What it counts

`ss -tan` prints one line per TCP socket, with the state in the first column. The script reads that column, skips the header, and counts ESTAB, TIME-WAIT, CLOSE-WAIT, LISTEN and the rest. The version in the GIF prints the three biggest states, from a read-only parse of text.

### The two flags

CLOSE-WAIT means the peer sent FIN and the application never closed its side. One is normal; a number that climbs is a leak, usually a connection pool or a handler that forgets to close. TIME-WAIT means the local side closed first and is waiting out the timer. It is normal on a busy client, but a spike can exhaust ephemeral ports.  
The defaults are 10 for CLOSE-WAIT and 1000 for TIME-WAIT, both adjustable. The script exits 1 when either count reaches its limit, 0 when clean, and 2 when the input cannot be read.

### How to use it

Run `ss -tan | python3 conn_state.py` on the node, or save the output and pass `--input`. Put it in cron every minute, or in a CI step against a captured fixture, and let the exit code fail the run.

> **The honest caveat:** ss is a snapshot. A leak is a trend, so keep the output and compare counts over time; a single TIME-WAIT number on a busy client proves very little.

> **The lesson:** name the state before you restart the pod.

## In one line

> **A leak has a shape.** CLOSE-WAIT is usually an app bug; TIME-WAIT is usually load.

**Run on the node**

```bash
ss -tan | python3 conn_state.py
```

## Script: conn_state.py

Download: [scripts/conn_state.py](../scripts/conn_state.py)

```python
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
```
