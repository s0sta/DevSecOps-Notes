---
id: p320
title: "A GPU utilisation report in Python"
slug: a-gpu-utilisation-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [GPU, Python, Observability, AIInfrastructure, SRE]
source: "LinkedIn post P320 · Visual series"
linkedin_date: 2028-10-12
design: code
script: gpu_report.py
---

# A GPU utilisation report in Python

The invoice says the cluster ran all month. The cards tell a different story: a queue that waited and cards that were not doing the work.

## Quick reference

The full script is at the end of this note: **gpu_report.py** (standard library only, no `pip install`).

**Run it**

```bash
python3 gpu_report.py < gpus.csv
```

**Example output**

```text
IDLE 1 OF 4 GPUS
ALERT 1 of 4 GPUs under 10%
```

## Explained

### What it runs

The script parses the CSV from `nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits`. Feed it a file, or pipe the live query in on stdin.

### What it prints

One row per GPU: the index, the name, utilisation as a percentage, and memory used as a share of total. A card below the threshold, ten percent by default, counts as idle. At the end it prints the count, and the exit code is 1 when any card is idle, so cron can log it and CI can fail on it.

### Why the memory column

A card at zero utilisation with most of its memory held is a stuck process, not an idle one. A card at high utilisation with almost no memory is usually a small kernel spinning. Neither shows up in a cluster-wide utilisation average.

### How to use it

Run it against a saved sample in CI, or every ten minutes from cron on each GPU node, appending to a log. Add `--json` for a dashboard, `--threshold` to match the shape of the workload, and -q when you only want the summary.

> **The honest caveat:** one nvidia-smi sample is one moment. A card at zero may be waiting on data, and a MIG instance reports its own slice, so sample over time before you call a GPU wasted.

> **The lesson:** utilisation is a time series, not a status field.

## In one line

> **An idle card is a finding.** A card at zero is either waiting or wasted; the log tells you which.

**Collect a sample**

```bash
nvidia-smi --query-gpu=utilization.gpu
```

## Script: gpu_report.py

Download: [scripts/gpu_report.py](../scripts/gpu_report.py)

```python
#!/usr/bin/env python3
"""gpu_report.py - report per-GPU utilisation from nvidia-smi and flag idle cards.

Parses the CSV from:

    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits

given as one or more files, or on stdin. For every GPU it prints the
utilisation, the memory used as a percentage of total, and a state. A card is
IDLE when its utilisation is below --threshold percent (default 10). The exit
code is 1 when any card is idle, so a cron job or a CI gate can act on it.

Read-only: it parses text and never talks to the driver. Exit codes: 0 every
GPU at or above the threshold, 1 at least one idle GPU, 2 usage or input
error.

Usage:
    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | python3 gpu_report.py -
    python3 gpu_report.py gpus.csv
    python3 gpu_report.py gpus.csv --threshold 20 --json
    python3 gpu_report.py a.csv b.csv --quiet

Cron (every ten minutes):
    */10 * * * * nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | python3 gpu_report.py - >> /var/log/gpu_report.log 2>&1

CI gate (fails when a card sits idle):
    python3 gpu_report.py gpus.csv --threshold 20

By s0sta.com
"""
import argparse
import json
import sys

PLACEHOLDERS = ("", "n/a", "[n/a]", "na", "[not supported]", "[unknown error]")


def as_float(value):
    """A number from an nvidia-smi field, or None for a placeholder."""
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in PLACEHOLDERS:
        return None
    try:
        return float(text)
    except ValueError:
        return "bad"


def parse_rows(text, label, errors):
    """Rows of (index, name, util, used, total) from one nvidia-smi dump."""
    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 5:
            errors.append("%s:%d: expected 5 comma-separated fields"
                          % (label, lineno))
            continue
        if parts[0].lower() == "index":
            continue  # header, when the query ran without noheader
        if not parts[0].isdigit():
            errors.append("%s:%d: index is not a number: %s"
                          % (label, lineno, parts[0]))
            continue
        name = ", ".join(parts[1:-3]) or "?"
        util = as_float(parts[-3])
        used = as_float(parts[-2])
        total = as_float(parts[-1])
        if util == "bad" or used == "bad" or total == "bad":
            errors.append("%s:%d: non-numeric memory or utilisation"
                          % (label, lineno))
            continue
        if total is not None and total <= 0:
            errors.append("%s:%d: memory.total must be > 0" % (label, lineno))
            continue
        rows.append({"index": int(parts[0]), "name": name, "util": util,
                     "used": used, "total": total})
    return rows


def state_of(util, threshold):
    """busy, IDLE or unknown for one utilisation reading."""
    if util is None:
        return "unknown"
    return "IDLE" if util < threshold else "busy"


def memory_pct(used, total):
    """Memory used as a percentage of total, or None when either is missing."""
    if used is None or not total:
        return None
    return 100.0 * used / total


def cards(count):
    """GPU or GPUs, so the summary line reads correctly for one card."""
    return "GPU" if count == 1 else "GPUs"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report per-GPU utilisation from nvidia-smi CSV and flag "
                    "cards below a threshold. Exits 1 when one is idle.")
    parser.add_argument("paths", nargs="*", default=["-"], metavar="PATH",
                        help="nvidia-smi CSV file(s), or - for stdin (default)")
    parser.add_argument("-t", "--threshold", type=float, default=10.0,
                        help="idle below this utilisation percentage (default 10)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only, no table")
    parser.add_argument("--json", action="store_true",
                        help="print one machine-readable JSON object")
    args = parser.parse_args(argv)

    if args.threshold < 0 or args.threshold > 100:
        parser.error("--threshold must be between 0 and 100")

    errors = []
    gpus = []
    for path in args.paths:
        label = "<stdin>" if path == "-" else path
        try:
            if path == "-":
                text = sys.stdin.read()
            else:
                with open(path, "r", encoding="utf-8") as handle:
                    text = handle.read()
        except OSError as exc:
            errors.append("%s: %s" % (label, exc))
            continue
        gpus.extend(parse_rows(text, label, errors))

    for message in errors:
        print("error: %s" % message, file=sys.stderr)
    if errors:
        return 2
    if not gpus:
        print("error: no GPU rows found", file=sys.stderr)
        return 2

    gpus.sort(key=lambda item: item["index"])
    for gpu in gpus:
        gpu["mem_pct"] = memory_pct(gpu["used"], gpu["total"])
        gpu["state"] = state_of(gpu["util"], args.threshold)
    idle = sum(1 for gpu in gpus if gpu["state"] == "IDLE")
    count = len(gpus)
    limit = ("%g" % args.threshold)

    if args.json:
        print(json.dumps({
            "count": count,
            "idle": idle,
            "threshold": args.threshold,
            "ok": idle == 0,
            "gpus": [{"index": gpu["index"], "name": gpu["name"],
                      "util": gpu["util"],
                      "mem_pct": (round(gpu["mem_pct"], 1)
                                  if gpu["mem_pct"] is not None else None),
                      "state": gpu["state"]} for gpu in gpus],
        }, sort_keys=True))
        return 1 if idle else 0

    if not args.quiet:
        print("%-4s %-28s %5s %7s   %s"
              % ("GPU", "NAME", "UTIL", "MEMORY", "STATE"))
        for gpu in gpus:
            util = "-" if gpu["util"] is None else "%d%%" % round(gpu["util"])
            mem = ("-" if gpu["mem_pct"] is None
                   else "%d%%" % round(gpu["mem_pct"]))
            print("%-4d %-28s %5s %7s   %s"
                  % (gpu["index"], gpu["name"][:28], util, mem, gpu["state"]))
        print()
    print("IDLE %d OF %d %s" % (idle, count, cards(count).upper()))
    if idle:
        print("ALERT %d of %d %s under %s%%"
              % (idle, count, cards(count), limit))
        return 1
    print("OK all %d %s at or above %s%%" % (count, cards(count), limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
