#!/usr/bin/env python3
"""Report top talkers, top ports and rejected flows from AWS VPC flow logs.

Usage:
    python3 flow_log_report.py flow.log
    aws logs tail /aws/vpc/flowlogs --follow | python3 flow_log_report.py -
    python3 flow_log_report.py flow.log --top 10 --max-reject-rate 0.02

Reads the default version 2 record, 14 space-separated fields:
    version account-id interface-id srcaddr dstaddr srcport dstport
    protocol packets bytes start end action log-status

Exit codes: 0 clean, 1 rejection rate over the threshold, 2 usage or input
error. The script is read-only: it never calls AWS and never writes a file.

Cron (daily at 06:10):
    10 6 * * * /usr/bin/python3 /opt/s0sta/flow_log_report.py /var/log/vpc-flow.log

CI:
    aws logs tail /aws/vpc/flowlogs --since 1h | python3 flow_log_report.py -

By s0sta.com
"""
import argparse
import sys
from collections import Counter


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(2)


def open_input(path):
    if path == "-":
        return sys.stdin
    try:
        return open(path, "r", encoding="utf-8", errors="replace")
    except OSError as exc:
        fail("cannot read %s: %s" % (path, exc))


def parse(lines):
    talkers = Counter()
    ports = Counter()
    accepts = 0
    rejects = 0
    skipped = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 14 or fields[0] != "2":
            skipped += 1
            continue
        action = fields[12].upper()
        status = fields[13].upper()
        if action not in ("ACCEPT", "REJECT") or status in ("NODATA", "SKIPDATA"):
            skipped += 1
            continue
        try:
            size = int(fields[9])
        except ValueError:
            skipped += 1
            continue
        talkers[(fields[3], fields[4])] += size
        ports[fields[6]] += 1
        if action == "ACCEPT":
            accepts += 1
        else:
            rejects += 1
    return talkers, ports, accepts, rejects, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Summarise AWS VPC flow log version 2 records: top talkers "
                    "by bytes, top destination ports, and rejected flows.")
    parser.add_argument("path", nargs="?", default="-",
                        help="flow log file, or - for stdin (default: -)")
    parser.add_argument("--top", type=int, default=5,
                        help="rows to show in each ranking (default: 5)")
    parser.add_argument("--max-reject-rate", type=float, default=0.05,
                        help="fail above this REJECT share, 0 to 1 (default: 0.05)")
    args = parser.parse_args(argv)

    if args.top < 1:
        parser.error("--top must be at least 1")
    if not 0 <= args.max_reject_rate <= 1:
        parser.error("--max-reject-rate must be between 0 and 1")

    stream = open_input(args.path)
    try:
        talkers, ports, accepts, rejects, skipped = parse(stream)
    finally:
        if stream is not sys.stdin:
            stream.close()

    total = accepts + rejects
    if not total:
        print("no usable version 2 records")
        return 0

    print("TOP TALKERS BY BYTES")
    for (source, destination), size in talkers.most_common(args.top):
        print("%s -> %s: %d bytes" % (source, destination, size))

    print("TOP DESTINATION PORTS")
    for port, count in ports.most_common(args.top):
        print("  %s  %d" % (port, count))

    rate = rejects / total
    print("REJECT %d of %d" % (rejects, total))
    print("reject rate %.1f%%" % (rate * 100))
    if skipped:
        print("skipped %d non-v2 or malformed lines" % skipped, file=sys.stderr)

    if rate > args.max_reject_rate:
        print("ALERT reject rate over %.1f%%" % (args.max_reject_rate * 100))
        return 1
    print("OK reject rate within %.1f%%" % (args.max_reject_rate * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
