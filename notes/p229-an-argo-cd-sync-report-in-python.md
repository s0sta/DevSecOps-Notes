---
id: p229
title: "An Argo CD sync report in Python"
slug: an-argo-cd-sync-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [GitOps, ArgoCD, Python, DevOps, SRE]
source: "LinkedIn post P229 · Platform series"
linkedin_date: 2028-03-14
design: code
script: argocd_report.py
---

# An Argo CD sync report in Python

A sync dashboard is fine until you need a number for a change record. Then you are scrolling the Argo CD UI during an incident, counting red rows by hand.

## Quick reference

The full script is at the end of this note: **argocd_report.py** (standard library only, no `pip install`).

**Run it**

```bash
argocd app list -o json | python3 argocd_report.py -
```

**Example output**

```text
shop-api  OutOfSync  Healthy
ALERT 3 of 12 need attention
```

## Explained

### What it does

The script reads `argocd app list -o json` from stdin or a file. For every app it compares status.sync.status and status.health.status, prints a line for anything that is not Synced and Healthy, then a count. Exit 1 means something needs attention, 0 means clean, 2 means bad JSON or a usage error. It is read-only: it never syncs, rolls back or writes to the cluster.

### Why JSON

The CLI's JSON is a stable contract, and it carries more than the table: labels, revisions, operation state. Text tables change between CLI versions; the JSON shape is what people script against. One pipe works on a laptop, in cron and in CI, with no screen scraping and no extra dependency.

### How to use it

`argocd app list -o json | python3 argocd_report.py -`. Or save the output and pass the file. In CI, run it after argocd app sync api, which waits by default, so the pipeline fails on the same state a human would see.

> **The honest caveat:** the script only knows what Argo CD knows. An app with no readiness probe can be Synced and Healthy while returning 500s, so pair the report with a real health signal.

> **The lesson:** a report turns a dashboard into an exit code, and an exit code can fail a pipeline.

## In one line

> **A dashboard is not an alert.** An app can be Synced and still be down.

**Pipe it in**

```bash
argocd app list -o json
```

## Script: argocd_report.py

Download: [scripts/argocd_report.py](../scripts/argocd_report.py)

```python
#!/usr/bin/env python3
"""argocd_report.py - a short GitOps sync report from Argo CD's JSON.

Reads `argocd app list -o json` from a file or stdin ('-'), prints every
Application that is not Synced and Healthy, and exits 1 if any need
attention. Read-only: it never syncs, rolls back or writes to the cluster.

Usage:
    argocd app list -o json | python3 argocd_report.py -
    argocd app list -o json > apps.json && python3 argocd_report.py apps.json
    python3 argocd_report.py -q apps.json      # summary only

CI (after a sync):
    argocd app sync api
    argocd app list -o json | python3 argocd_report.py -

Cron (every 15 minutes):
    */15 * * * * argocd app list -o json | python3 /opt/scripts/argocd_report.py -q - \
        >> /var/log/argocd_report.log 2>&1

Exit codes: 0 all Synced and Healthy, 1 something needs attention, 2 usage
or input error.

By s0sta.com
"""
import argparse
import json
import sys

def load(path):
    """Return a list of Application objects from Argo CD's JSON."""
    if path == "-":
        raw = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    if not raw.strip():
        raise ValueError("empty input")
    data = json.loads(raw)
    if isinstance(data, dict):
        data = data.get("items")
        if not isinstance(data, list):
            raise ValueError("JSON object has no items list")
    if not isinstance(data, list):
        raise ValueError("expected a JSON array of Applications")
    if not all(isinstance(app, dict) for app in data):
        raise ValueError("expected Application objects in the array")
    return data


def state(app):
    """Return (sync, health) for one Application, tolerating missing fields."""
    status = app.get("status") or {}
    sync = (status.get("sync") or {}).get("status", "Unknown")
    health = (status.get("health") or {}).get("status", "Unknown")
    return sync, health


def main():
    ap = argparse.ArgumentParser(
        description="Report Argo CD apps that are not Synced and Healthy.",
        epilog="Read-only. Exit 0 clean, 1 attention needed, 2 input error.",
    )
    ap.add_argument("path", nargs="?", default="-",
                    help="JSON file from 'argocd app list -o json', or - for stdin")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="print the summary only")
    args = ap.parse_args()

    try:
        apps = load(args.path)
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    rows = []
    for app in apps:
        sync, health = state(app)
        if sync != "Synced" or health != "Healthy":
            name = (app.get("metadata") or {}).get("name", "?")
            rows.append((name, sync, health))
    rows.sort()

    out_of_sync = sum(1 for _, sync, _ in rows if sync != "Synced")
    unhealthy = sum(1 for _, _, health in rows if health != "Healthy")
    attention = len(rows)

    if not args.quiet and rows:
        print("%-28s %-12s %s" % ("APP", "SYNC", "HEALTH"))
        for name, sync, health in rows:
            print("%-28s %-12s %s" % (name, sync, health))
        print()

    print("checked %d apps: %d out of sync, %d unhealthy"
          % (len(apps), out_of_sync, unhealthy))
    if attention:
        print("ALERT %d of %d apps need attention" % (attention, len(apps)))
        return 1
    print("OK %d apps Synced and Healthy" % len(apps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
