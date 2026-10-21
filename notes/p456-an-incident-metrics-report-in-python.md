---
id: p456
title: "An incident metrics report in Python"
slug: an-incident-metrics-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [SRE, IncidentResponse, Python, DevOps, Reliability]
source: "LinkedIn post P456 · DevOps series"
linkedin_date: 2029-08-26
design: code
script: incident_metrics.py
---

# An incident metrics report in Python

An incident ends and the channel goes quiet, but the timestamps stay behind. Read as a set, they say where the response was slow: detection, acknowledgement or recovery.

## Quick reference

The full script is at the end of this note: `incident_metrics.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 incident_metrics.py incidents.jsonl
```

**Example output**

```text
sev2     3        6m      21m    1h20m  15m/4h
BREACH sev2 MTTA 21m > 15m
```

## Explained

### What it measures

MTTD is the gap from impact (started_at) to detection (detected_at). MTTA is detection to acknowledgement (acked_at). MTTR is impact to service restored (mitigated_at), not to the moment the ticket closed (resolved_at). The script prints the median of each, per severity, because one long incident drags a mean somewhere useless.

### Why medians

A single 40-minute SEV1 among four five-minute ones moves the mean from five minutes to twelve and says nothing about the typical night. The median answers the question people actually ask: what a normal incident of this level looks like.

### The SLA gate

Each severity has an acknowledgement window and a restore window: five minutes and one hour for SEV1, fifteen minutes and four hours for SEV2, one hour and one day for SEV3. `python3 incident_metrics.py incidents.jsonl` exits 1 when a median misses its window. The frame runs the acknowledgement check; the attached tool runs the restore check too. Exit 0 means everything is inside, and 2 is an incomplete record or timestamps that run backwards.

> **The honest caveat:** without started_at, MTTD cannot be measured at all, and a team that skips it reports a detection time of zero. Record when impact began, not only when the alert fired.

> **The lesson:** a timestamp you never wrote is a metric you will never have.

## In one line

> **Measure the wait, not the story.** Four timestamps answer the question a retro argues about.

**Stamp the start:** started_at, not just detected_at

## Script: incident_metrics.py

Download: [scripts/incident_metrics.py](../scripts/incident_metrics.py)

```python
#!/usr/bin/env python3
"""Report incident detection, acknowledgement and recovery medians from JSONL.

Usage:
    python3 incident_metrics.py incidents.jsonl
    python3 incident_metrics.py incidents.jsonl --json
    python3 incident_metrics.py incidents.jsonl --sla sev2=10,180
    python3 incident_metrics.py --help

Each line is one closed incident:

    {"severity": "sev2",
     "started_at": "2026-04-14T09:05:00+00:00",
     "detected_at": "2026-04-14T09:19:00+00:00",
     "acked_at": "2026-04-14T09:24:00+00:00",
     "mitigated_at": "2026-04-14T11:02:00+00:00",
     "resolved_at": "2026-04-14T13:40:00+00:00"}

started_at is when customer impact began; without it MTTD cannot be
measured. detected_at is when a signal or a person noticed, acked_at is the
acknowledgement, mitigated_at is when service was restored, resolved_at is
when the incident was closed.

The report prints, per severity, the median MTTD (started to detected), MTTA
(detected to acknowledged) and MTTR (started to mitigated). The SLA gate uses
two windows per severity: acknowledgement and restore, in minutes. Defaults:

    sev1   5 / 60        sev2  15 / 240
    sev3  60 / 1440      sev4 240 / 4320

Override one severity with --sla sev2=10,180 (ack_minutes,restore_minutes).
An unknown severity is reported without a gate.

Exit codes: 0 every median inside its window, 1 a median over a window,
2 usage or input error (missing field, bad timestamp, times out of order).
Read-only: the file is opened for reading and never written.

Cron: 0 7 * * 1 python3 /opt/s0sta/incident_metrics.py /var/tmp/closed.jsonl
CI:   python3 incident_metrics.py incidents.jsonl --sla sev1=5,60

By s0sta.com
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone

FIELDS = ("severity", "started_at", "detected_at", "acked_at",
          "mitigated_at", "resolved_at")
SLA_MINUTES = {
    "sev1": (5, 60),
    "sev2": (15, 240),
    "sev3": (60, 1440),
    "sev4": (240, 4320),
}


class InputError(Exception):
    """An input line or argument that cannot be used."""


def parse_when(value, where, field):
    """Parse an ISO 8601 timestamp into an aware UTC datetime."""
    text = str(value or "").strip()
    if not text:
        raise InputError("%s: %s is empty" % (where, field))
    try:
        when = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise InputError("%s: bad %s %r (expected ISO 8601)"
                         % (where, field, value))
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


def load_incidents(path):
    """Read the JSONL file and return one dict per incident, in minutes."""
    try:
        handle = open(path, "r", encoding="utf-8")
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    incidents = []
    with handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            where = "%s line %d" % (path, number)
            try:
                row = json.loads(line)
            except ValueError:
                raise InputError("%s: not valid JSON" % where)
            if not isinstance(row, dict):
                raise InputError("%s: expected a JSON object" % where)
            missing = [name for name in FIELDS
                       if not str(row.get(name, "")).strip()]
            if missing:
                raise InputError("%s: missing %s"
                                 % (where, ", ".join(missing)))
            stamps = {name: parse_when(row[name], where, name)
                      for name in FIELDS if name != "severity"}
            started = stamps["started_at"]
            detected = stamps["detected_at"]
            acked = stamps["acked_at"]
            mitigated = stamps["mitigated_at"]
            resolved = stamps["resolved_at"]
            for first, second in (("started_at", "detected_at"),
                                  ("detected_at", "acked_at"),
                                  ("detected_at", "mitigated_at"),
                                  ("mitigated_at", "resolved_at")):
                if stamps[second] < stamps[first]:
                    raise InputError("%s: %s is before %s"
                                     % (where, second, first))
            incidents.append({
                "severity": str(row["severity"]).strip().lower(),
                "mttd": (detected - started).total_seconds() / 60.0,
                "mtta": (acked - detected).total_seconds() / 60.0,
                "mttr": (mitigated - started).total_seconds() / 60.0,
                "close": (resolved - started).total_seconds() / 60.0,
            })
    return incidents


def parse_sla(values):
    """Start from the default windows and apply --sla overrides."""
    table = dict(SLA_MINUTES)
    for item in values:
        key, sep, rest = item.partition("=")
        key = key.strip().lower()
        parts = rest.split(",")
        if not sep or not key or len(parts) != 2:
            raise InputError("--sla expects sev2=15,240, got %r" % item)
        try:
            ack, restore = int(parts[0]), int(parts[1])
        except ValueError:
            raise InputError("--sla windows must be whole minutes: %r" % item)
        if ack < 0 or restore < 0:
            raise InputError("--sla windows cannot be negative: %r" % item)
        table[key] = (ack, restore)
    return table


def human(minutes):
    """Format a duration in minutes as 7m, 2h05m or 3d02h."""
    total = int(round(minutes))
    if total < 60:
        return "%dm" % total
    hours, mins = divmod(total, 60)
    if hours < 24:
        return "%dh" % hours if mins == 0 else "%dh%02dm" % (hours, mins)
    days, hours = divmod(hours, 24)
    return "%dd" % days if hours == 0 else "%dd%02dh" % (days, hours)


def summarise(incidents):
    """Median MTTD, MTTA and MTTR per severity."""
    groups = defaultdict(lambda: {"n": 0, "mttd": [], "mtta": [], "mttr": [],
                                 "close": []})
    for incident in incidents:
        group = groups[incident["severity"]]
        group["n"] += 1
        group["mttd"].append(incident["mttd"])
        group["mtta"].append(incident["mtta"])
        group["mttr"].append(incident["mttr"])
        group["close"].append(incident["close"])
    report = {}
    for severity, group in groups.items():
        report[severity] = {
            "n": group["n"],
            "mttd": statistics.median(group["mttd"]),
            "mtta": statistics.median(group["mtta"]),
            "mttr": statistics.median(group["mttr"]),
            "close": statistics.median(group["close"]),
        }
    return report


def find_breaches(report, sla):
    """Return a list of (severity, metric, median, window) breaches."""
    breaches = []
    for severity in sorted(report):
        windows = sla.get(severity)
        if not windows:
            continue
        ack_window, restore_window = windows
        row = report[severity]
        if row["mtta"] > ack_window:
            breaches.append((severity, "mtta", row["mtta"], ack_window))
        if row["mttr"] > restore_window:
            breaches.append((severity, "mttr", row["mttr"], restore_window))
    return breaches


def print_table(report, breaches, sla):
    print("%-6s %3s  %8s %8s %8s  %s"
          % ("sev", "n", "mttd", "mtta", "mttr", "sla ack/restore"))
    for severity in sorted(report):
        row = report[severity]
        windows = sla.get(severity)
        window_text = ("%s/%s" % (human(windows[0]), human(windows[1]))
                       if windows else "-")
        print("%-6s %3d  %8s %8s %8s  %s"
              % (severity, row["n"], human(row["mttd"]), human(row["mtta"]),
                 human(row["mttr"]), window_text))
    for severity, metric, median, window in breaches:
        print("BREACH %s %s %s > %s"
              % (severity, metric.upper(), human(median), human(window)))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Report median MTTD, MTTA and MTTR per severity from an "
                    "incidents JSONL file.",
        epilog="Exit 0 inside SLA, 1 a breach, 2 usage or input. By s0sta.com")
    parser.add_argument("path", help="incidents JSONL, one incident per line")
    parser.add_argument("--sla", action="append", default=[], metavar="SEV=A,R",
                        help="ack and restore windows in minutes, e.g. "
                             "sev2=10,180; repeatable")
    parser.add_argument("--json", action="store_true",
                        help="print a JSON report instead of a table")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        sla = parse_sla(args.sla)
        incidents = load_incidents(args.path)
    except InputError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2
    report = summarise(incidents)
    breaches = find_breaches(report, sla)

    if args.json:
        print(json.dumps({
            "incidents": len(incidents),
            "sla_minutes": {key: list(value) for key, value in sla.items()},
            "severity": report,
            "breaches": [{"severity": s, "metric": m, "median_minutes": v,
                          "window_minutes": w}
                         for s, m, v, w in breaches],
        }, indent=2, sort_keys=True))
    else:
        print_table(report, breaches, sla)
    return 1 if breaches else 0


if __name__ == "__main__":
    sys.exit(main())
```
