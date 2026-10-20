#!/usr/bin/env python3
"""log_latency.py - p50/p95/p99 and 5xx rate from an nginx access log.

Parses the nginx combined log format with $request_time appended as the last
field. The matching log_format is:

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" $request_time';

Reads a file or stdin ('-'), prints p50/p95/p99 in milliseconds and the 5xx
rate, and exits 1 when p99 or the 5xx rate is over the thresholds. Read-only.

Usage:
    python3 log_latency.py access.log
    cat access.log | python3 log_latency.py -
    python3 log_latency.py access.log --p99-ms 800 --max-5xx 2

CI (after a deploy):
    cat /var/log/nginx/access.log | python3 log_latency.py - --p99-ms 800

Cron (yesterday's log, 06:00):
    0 6 * * * python3 /opt/scripts/log_latency.py /var/log/nginx/access.log.1 \
        >> /var/log/latency.log 2>&1

Exit codes: 0 within thresholds, 1 over a threshold, 2 usage or no data.

By s0sta.com
"""
import argparse
import math
import re
import sys

# Closing quote of the request line, status, body bytes, referer, user agent,
# then $request_time in seconds at the end of the line.
LINE = re.compile(
    r'"\s+(?P<status>[1-5]\d{2})\s+\d+\s+"[^"]*"\s+"[^"]*"\s+'
    r'(?P<rt>\d+(?:\.\d+)?)\s*$'
)


def percentile(values, q):
    """Nearest-rank percentile of a sorted list. q is 0-100."""
    if not values:
        return 0.0
    rank = max(1, math.ceil(q / 100.0 * len(values)))
    return values[rank - 1]


def report(total, skipped, statuses, times, p99_ms, max_5xx):
    n = len(times)
    bad = sum(1 for s in statuses if s.startswith("5"))
    rate = 100.0 * bad / n
    times.sort()
    p50 = percentile(times, 50)
    p95 = percentile(times, 95)
    p99 = percentile(times, 99)

    print("parsed %d  skipped %d  5xx %d (%.2f%%)" % (total, skipped, bad, rate))
    print("p50 %.0fms  p95 %.0fms  p99 %.0fms" % (p50, p95, p99))

    problems = []
    if p99 > p99_ms:
        problems.append("p99 %.0fms over %.0fms" % (p99, p99_ms))
    if rate > max_5xx:
        problems.append("5xx %.2f%% over %.1f%%" % (rate, max_5xx))
    if problems:
        for problem in problems:
            print("ALERT " + problem)
        return 1
    print("OK p99 %.0fms within %.0fms, 5xx %.2f%% within %.1f%%"
          % (p99, p99_ms, rate, max_5xx))
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="p50/p95/p99 and 5xx rate from an nginx access log.",
        epilog="Read-only. Exit 0 clean, 1 over a threshold, 2 usage or no data.",
    )
    ap.add_argument("log", nargs="?", default="-",
                    help="access log file, or - for stdin (default)")
    ap.add_argument("--p99-ms", type=float, default=1000.0,
                    help="p99 threshold in milliseconds (default 1000)")
    ap.add_argument("--max-5xx", type=float, default=5.0,
                    help="5xx rate threshold in percent (default 5)")
    args = ap.parse_args()

    if args.p99_ms < 0 or args.max_5xx < 0:
        print("error: thresholds must not be negative", file=sys.stderr)
        return 2

    if args.log == "-":
        fh = sys.stdin
        close = False
    else:
        try:
            fh = open(args.log, encoding="utf-8", errors="replace")
        except OSError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 2
        close = True

    total = skipped = 0
    statuses, times = [], []
    try:
        for line in fh:
            total += 1
            match = LINE.search(line)
            if not match:
                skipped += 1
                continue
            statuses.append(match.group("status"))
            times.append(float(match.group("rt")) * 1000.0)
    finally:
        if close:
            fh.close()

    if not times:
        print("error: no timed requests found; add $request_time to the "
              "nginx log_format", file=sys.stderr)
        return 2

    return report(total, skipped, statuses, times, args.p99_ms, args.max_5xx)


if __name__ == "__main__":
    sys.exit(main())
