---
id: p355
title: "A consumer lag report in Python"
slug: a-consumer-lag-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Kafka, Python, DataEngineering, SRE, Observability]
source: "LinkedIn post P355 · Data series"
linkedin_date: 2029-01-02
design: code
script: consumer_lag.py
---

# A consumer lag report in Python

One consumer group is three days behind and the dashboard is green. `kafka-consumer-groups --describe` prints the lag, but it prints one row per partition, and nobody adds those up by hand.

## Quick reference

The full script is at the end of this note: **consumer_lag.py** (standard library only, no `pip install`).

**Run it**

```bash
kafka-consumer-groups --describe --group g|./consumer_lag.py
```

**Example output**

```text
billing              invoices                 1190
billing 1190 OVER
```

## Explained

**What it reads**  
The script takes the plain describe output on stdin. Each row is a group, a topic, a partition, the current offset, the log-end offset and the lag. Rows for a group with no committed offsets carry a dash instead of a number, the header starts with GROUP, and the parser skips both.

**What it sums**  
Every row with a numeric lag is added to a per-group-and-topic total and to a per-group total. The report prints the topic rows first, then one line per group marked OVER or ok.

**The exit code**  
Exit 0 means every group is inside the budget, exit 1 means at least one is over it, and exit 2 means the input was unreadable or held no lag rows. Exit 2 is a broken check, not a clean result, and CI should treat it that way. The attached script is standard library only, read-only, and takes `--limit` and `--group`.

> **The honest caveat:** describe is a snapshot from one broker. A group with no active members still reports its last committed offsets, and a recreated group starts again at zero, so the trend matters more than one number.

> **The lesson:** a lag number you have to assemble by hand is a lag number nobody checks.

## In one line

> **Lag is the only honest metric.** A green dashboard with a growing lag is a dashboard lying.

**Run it in ci**

```bash
python3 consumer_lag.py lag.txt --limit 500
```

## Script: consumer_lag.py

Download: [scripts/consumer_lag.py](../scripts/consumer_lag.py)

```python
#!/usr/bin/env python3
"""Report Kafka consumer lag from kafka-consumer-groups --describe output.

Reads the plain (non-verbose) output of

    kafka-consumer-groups --bootstrap-server localhost:9092 \
        --describe --group api-consumers

from a file or from stdin, adds up LAG per group and topic, and exits 1
when a group's total lag is over the limit.

Usage:
    kafka-consumer-groups --describe --group api-consumers > lag.txt
    python3 consumer_lag.py lag.txt --limit 500

    kafka-consumer-groups --describe --group api-consumers \
        | python3 consumer_lag.py - --limit 500

Exit codes:
    0  every group is at or under the limit
    1  at least one group is over it
    2  unreadable input, bad arguments or no lag rows at all

Cron/CI:
    0 * * * * kafka-consumer-groups --describe --group api-consumers \
        | python3 /srv/checks/consumer_lag.py - --limit 500

By s0sta.com
"""
import argparse
import sys

HEADER = "GROUP"


def lag_rows(lines):
    """Return (group, topic, lag) for each partition row with a numeric LAG."""
    rows = []
    for line in lines:
        parts = line.split()
        # group, topic, partition, current-offset, log-end-offset, lag, ...
        if len(parts) < 6 or parts[0] == HEADER:
            continue
        lag = parts[5]
        if not lag.isdigit():
            continue
        rows.append((parts[0], parts[1], int(lag)))
    return rows


def report(rows, limit):
    """Print the report and return 0 when inside the limit, 1 when over."""
    by_topic, by_group = {}, {}
    for name, topic, lag in rows:
        by_topic[(name, topic)] = by_topic.get((name, topic), 0) + lag
        by_group[name] = by_group.get(name, 0) + lag

    print("%-24s %-24s %8s" % ("GROUP", "TOPIC", "LAG"))
    for (name, topic), lag in sorted(by_topic.items()):
        print("%-24s %-24s %8d" % (name, topic, lag))

    over = [(g, n) for g, n in sorted(by_group.items()) if n > limit]
    print("")
    for name, lag in sorted(by_group.items()):
        print("%-24s %8d  %s" % (name, lag, "OVER" if lag > limit else "ok"))
    print("%d of %d groups over %d" % (len(over), len(by_group), limit))
    return 1 if over else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="consumer_lag.py",
        description="Sum Kafka consumer lag per group and topic from the output "
                    "of kafka-consumer-groups --describe.")
    parser.add_argument("source", nargs="?", default="-",
                        help="describe output file, or - for stdin (default: -)")
    parser.add_argument("--limit", type=int, default=1000, metavar="N",
                        help="lag a group may carry before failing (default: 1000)")
    parser.add_argument("--group", metavar="NAME",
                        help="only report this consumer group")
    args = parser.parse_args(argv)

    if args.limit < 0:
        parser.error("--limit must be zero or more")

    try:
        if args.source == "-":
            lines = sys.stdin.read().splitlines()
        else:
            with open(args.source) as handle:
                lines = handle.read().splitlines()
    except OSError as exc:
        print("error: cannot read %s: %s" % (args.source, exc), file=sys.stderr)
        return 2

    rows = lag_rows(lines)
    if not rows:
        print("error: no lag rows found; is this kafka-consumer-groups "
              "--describe output?", file=sys.stderr)
        return 2

    if args.group:
        rows = [r for r in rows if r[0] == args.group]
        if not rows:
            print("error: group %s is not in the input" % args.group,
                  file=sys.stderr)
            return 2

    return report(rows, args.limit)


if __name__ == "__main__":
    sys.exit(main())
```
