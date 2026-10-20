---
id: p239
title: "A Prometheus health check in Python"
slug: a-prometheus-health-check-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Prometheus, Python, SRE, Observability, DevOps]
source: "LinkedIn post P239 · Platform series"
linkedin_date: 2028-04-06
design: code
script: prom_check.py
---

# A Prometheus health check in Python

A Grafana dashboard is on the wall screen and nobody has looked at it since Tuesday. A firing alert and a dead scrape target are facts you can check from a pipeline, and this script does exactly that.

## Quick reference

The full script is at the end of this note: **prom_check.py** (standard library only, no `pip install`).

**Run it**

```bash
python3 prom_check.py http://prometheus:9090
```

**Example output**

```text
ALERT 2 firing, 1 down
```

## Explained

### What it does

It calls two read-only Prometheus endpoints: /api/v1/alerts for the alerts Prometheus is holding, and /api/v1/targets?state=active for everything it is scraping. It counts the alerts in state firing and the targets whose health is not up, prints them, and exits 1 if either list is non-empty. The full script is attached: standard library only, read-only requests.

### Why these two

Alerts prove a rule has been true long enough to fire. Targets prove the monitoring itself is working, which is the failure nobody alerts on: a down target is a blind spot where the metrics you rely on stop arriving. A dashboard cannot fail a deploy, and a green board is not evidence.

### How to use it

`python3 prom_check.py http://prometheus:9090`, from cron every five minutes or as the last step of a deploy. It exits 0 when clean, 1 when something is firing or down, and 2 when the request fails, which is not the same as healthy.

> **The honest caveat:** it reports what Prometheus knows. A rule with a long for: or a scrape interval of five minutes will still look green while users wait.

> **The lesson:** monitor the monitor, with something that can fail a build.

## In one line

> **A dashboard is not a check.** If nobody reads it at 3 a.m., it is decoration.

**Run it in ci**

```bash
python3 prom_check.py $PROM_URL
```

## Script: prom_check.py

Download: [scripts/prom_check.py](../scripts/prom_check.py)

```python
#!/usr/bin/env python3
"""prom_check.py - fail when Prometheus has firing alerts or targets that are down.

Reads two read-only endpoints from the Prometheus HTTP API:

    /api/v1/alerts                every alert Prometheus is holding
    /api/v1/targets?state=active  every target it is scraping

Exit codes: 0 clean, 1 firing alerts or targets not up, 2 usage or request
error. GET requests only; nothing is written. Standard library only.

Usage:
    python3 prom_check.py
    python3 prom_check.py http://prometheus:9090
    python3 prom_check.py -t 10 -q
    python3 prom_check.py --alerts alerts.json --targets targets.json
    cat alerts.json | python3 prom_check.py --alerts - --targets targets.json
    python3 prom_check.py --json

Cron / CI (a non-zero exit is the signal):
    */5 * * * * python3 prom_check.py -q >> /var/log/prom_check.log || \
        mail -s "prometheus unhealthy" oncall@example.com < /var/log/prom_check.log
    python3 prom_check.py "$PROM_URL" || exit 1

The default base URL is http://localhost:9090, or $PROM_URL when it is set.

By s0sta.com
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "http://localhost:9090"


class CheckError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source, timeout):
    """Read one JSON document from a URL, a file, or '-' for stdin."""
    if source == "-":
        try:
            return json.load(sys.stdin)
        except ValueError as exc:
            raise CheckError("stdin is not JSON: %s" % exc)

    if "://" in source:
        try:
            with urllib.request.urlopen(source, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise CheckError("%s returned HTTP %s" % (source, exc.code))
        except urllib.error.URLError as exc:
            raise CheckError("%s unreachable: %s" % (source, exc.reason))
        except OSError as exc:
            raise CheckError("%s failed: %s" % (source, exc))
        except ValueError as exc:
            raise CheckError("%s did not return JSON: %s" % (source, exc))

    try:
        with open(source) as handle:
            return json.load(handle)
    except OSError as exc:
        raise CheckError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise CheckError("%s is not JSON: %s" % (source, exc))


def data_of(doc, what):
    """Return the data object of a Prometheus API response, or fail."""
    if not isinstance(doc, dict) or doc.get("status") != "success":
        raise CheckError("%s: API did not return status=success" % what)
    data = doc.get("data")
    if not isinstance(data, dict):
        raise CheckError("%s: response has no data object" % what)
    return data


def label(item, name, fallback="(none)"):
    labels = item.get("labels") or {}
    return labels.get(name) or fallback


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check the Prometheus API for firing alerts and targets that are not up.",
        epilog="Exit codes: 0 clean, 1 findings, 2 usage or request error.")
    parser.add_argument("url", nargs="?", default=None,
                        help="Prometheus base URL, default $PROM_URL or %s" % DEFAULT_URL)
    parser.add_argument("-t", "--timeout", type=float, default=5.0,
                        help="seconds per request, default 5")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON report instead of text")
    parser.add_argument("--alerts", metavar="SOURCE",
                        help="read the /api/v1/alerts response from a URL, file or -")
    parser.add_argument("--targets", metavar="SOURCE",
                        help="read the /api/v1/targets response from a URL, file or -")
    args = parser.parse_args(argv)

    if args.alerts == "-" and args.targets == "-":
        parser.error("--alerts and --targets cannot both read from stdin")

    base = (args.url or os.environ.get("PROM_URL") or DEFAULT_URL).rstrip("/")
    alerts_src = args.alerts or base + "/api/v1/alerts"
    targets_src = args.targets or base + "/api/v1/targets?state=active"

    try:
        alerts_data = data_of(read_json(alerts_src, args.timeout), "alerts")
        targets_data = data_of(read_json(targets_src, args.timeout), "targets")
    except CheckError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    alerts = alerts_data.get("alerts") or []
    targets = targets_data.get("activeTargets") or []
    if not isinstance(alerts, list) or not isinstance(targets, list):
        print("ERR API data is not shaped as expected", file=sys.stderr)
        return 2
    alerts = [a for a in alerts if isinstance(a, dict)]
    targets = [t for t in targets if isinstance(t, dict)]

    firing = [a for a in alerts if a.get("state") == "firing"]
    pending = [a for a in alerts if a.get("state") == "pending"]
    down = [t for t in targets if t.get("health") != "up"]

    if args.json:
        report = {
            "ok": not (firing or down),
            "firing": [{"alertname": label(a, "alertname"),
                        "severity": label(a, "severity", ""),
                        "activeAt": a.get("activeAt", "")} for a in firing],
            "down": [{"job": label(t, "job"),
                      "instance": label(t, "instance"),
                      "scrapeUrl": t.get("scrapeUrl", ""),
                      "health": t.get("health", "")} for t in down],
            "pending": len(pending),
            "targets": len(targets),
        }
        print(json.dumps(report, indent=None if args.quiet else 2, sort_keys=True))
    else:
        if firing or down:
            print("ALERT %d firing, %d down" % (len(firing), len(down)))
        else:
            print("OK no firing alerts, %d targets up" % len(targets))
        if not args.quiet:
            for alert in firing:
                print("  firing  %s  severity=%s" %
                      (label(alert, "alertname"), label(alert, "severity", "-")))
            for target in down:
                print("  down    %s  %s  (%s)" %
                      (label(target, "job"), label(target, "instance"),
                       target.get("health", "unknown")))

    return 1 if (firing or down) else 0


if __name__ == "__main__":
    sys.exit(main())
```
