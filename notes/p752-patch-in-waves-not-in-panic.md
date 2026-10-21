---
id: p752
title: "Patch in waves, not in panic"
slug: patch-in-waves-not-in-panic
sections: [devsecops]
topic: "Python scripts"
tags: [VulnerabilityManagement, PatchManagement, DevOps, Python, CyberSecurity]
source: "LinkedIn post P752 · ASM series"
linkedin_date: 2031-07-17
design: code
script: patch_waves.py
---

# Patch in waves, not in panic

The scanner returns 2,000 findings, someone sorts by CVSS, and the board is asked for 247 patches in one weekend. The board refuses, and nothing ships.

## Quick reference

The full script is at the end of this note: `patch_waves.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 patch_waves.py findings.json
```

**Example output**

```text
BLOCKED 2 findings: 1 no fix version, 1 no owner
FAIL wave now: 9 items over max 8
```

## Explained

### What it does

`patch_waves.py` reads a findings export. Critical findings go to the now wave, high to this sprint, the rest later. Inside a wave it groups rows by owner, service and fix version, so one ticket covers every host on the same build, and prints the blast radius: findings, assets and services. A row with no fix version or owner is blocked and counted separately.

### What the screen shows

The fourteen lines count the blocked rows by reason and the critical rows that can be scheduled. The last two read BLOCKED 2 findings: 1 no fix version, 1 no owner, then FAIL wave now: 9 items over max 8, and exit 1.

### How to run it

`python3 patch_waves.py findings.json`, with `--max-items 5` for a tighter window. CI fails the plan when a wave is too big; a Monday cron rebuilds it.

### The fix

Split the now wave by service, or move a group to the next window. Then chase the blocked rows: the vendor for the fix, the owner for the name.

### Prevention

Cap every wave and keep the blocked queue beside it. A wave that grows every week is a plan nobody reads.

> **The honest caveat:** severity is the scanner's label, so a critical with no fix version is a vendor conversation. `--max-items` is a policy choice.

> **The lesson:** a patch plan is a queue with a size.

## In one line

> **Patch in waves, not in panic.** A wave is a change window, not a wish list.

**Rebuild the plan**

```bash
python3 patch_waves.py findings.json
```

## Script: patch_waves.py

Download: [scripts/patch_waves.py](../scripts/patch_waves.py)

```python
#!/usr/bin/env python3
"""Turn a findings export into patch waves a change window can carry.

Reads a vulnerability-management export as JSON:

    {"findings": [
        {"id": "F-1001", "asset": "api-01", "service": "api",
         "owner": "platform", "severity": "critical",
         "fix_version": "1.24.0"},
        ...]}

Every finding is grouped by owner, service and fix version, then placed in
one of three waves:

    now      critical
    sprint   high
    later    medium and low

Each wave reports its blast radius: how many findings, assets and services
it touches, plus the largest owner/service/version group in it. A wave larger
than --max-items is a change window nobody can review, so the run exits 1 and
the wave has to be split.

A finding with no owner or no fix version is not put in a wave. It is counted
as blocked, because neither a change ticket nor a deployment can be opened for
it. A finding with both problems is counted under no fix version: without a
fix, even a named owner cannot schedule the change. Blocked findings do not
fail the run on their own; they are a separate queue with a different owner.

Usage:
    scanner-export > /tmp/findings.json
    python3 patch_waves.py /tmp/findings.json
    python3 patch_waves.py /tmp/findings.json --max-items 5
    cat /tmp/findings.json | python3 patch_waves.py -

Exit codes: 0 every wave fits, 1 a wave exceeds --max-items, 2 usage or
invalid input.

CI (fail the plan when a wave cannot be reviewed):
    python3 patch_waves.py findings.json --max-items 8

Cron (Monday morning, rebuild the plan from the weekly export):
    0 7 * * 1 python3 /opt/s0sta/patch_waves.py /exports/findings.json --max-items 8

The script is read-only: one JSON file or stdin, no scanner, no API calls, no
writes. It does not decide whether a finding is real or how urgent it is; it
only decides what fits in a window. --max-items is a policy choice, not a
technical limit: set it to what the change board can review in one sitting.
Severity is taken from the export, so a mislabelled finding lands in the wrong
wave.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys
from collections import Counter

WAVE_OF = {"critical": "now", "high": "sprint", "medium": "later",
           "low": "later"}
WAVE_ORDER = ("now", "sprint", "later")
MISSING_FIX = ("", "none", "n/a", "na", "unknown", "-", "null")


class WaveError(Exception):
    """Anything that should end the run with exit code 2."""


def load_json(source, label):
    """Read JSON from a path, or stdin when source is '-'."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise WaveError("cannot read %s: %s" % (label, exc))
    except ValueError as exc:
        raise WaveError("%s is not valid JSON: %s" % (label, exc))


def text_field(item, key, label):
    """Return a stripped string field, treating null as empty."""
    value = item.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise WaveError("%s must be a string" % label)
    return value.strip()


def read_findings(doc):
    """Validate the export and return one row per finding."""
    if isinstance(doc, dict):
        doc = doc.get("findings")
    if not isinstance(doc, list):
        raise WaveError("the export must be a list or an object with findings")
    rows = []
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise WaveError("finding %d is not an object" % number)
        fid = item.get("id") or "finding %d" % number
        if not isinstance(fid, str):
            raise WaveError("finding %d id must be a string" % number)
        fid = fid.strip()
        asset = text_field(item, "asset", "%s asset" % fid)
        service = text_field(item, "service", "%s service" % fid)
        owner = text_field(item, "owner", "%s owner" % fid)
        fix = text_field(item, "fix_version", "%s fix_version" % fid)
        severity = text_field(item, "severity", "%s severity" % fid).lower()
        if not asset or not service:
            raise WaveError("%s needs an asset and a service" % fid)
        if severity not in WAVE_OF:
            raise WaveError("%s has unknown severity %r" % (fid, severity))
        rows.append({"id": fid, "asset": asset, "service": service,
                     "owner": owner, "fix": fix, "severity": severity})
    return rows


def build_plan(rows):
    """Return the three waves and the blocked list."""
    waves = {wave: [] for wave in WAVE_ORDER}
    blocked = []
    for row in rows:
        if row["fix"].lower() in MISSING_FIX:
            blocked.append("no fix version")
            continue
        if not row["owner"]:
            blocked.append("no owner")
            continue
        waves[WAVE_OF[row["severity"]]].append(row)
    return waves, blocked


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Group findings into patch waves by owner, service and "
                    "fix version, and fail when a wave is too large.",
        epilog="Exit codes: 0 every wave fits, 1 a wave exceeds --max-items, "
               "2 usage or input error.")
    parser.add_argument("findings", help="findings JSON export, or - for stdin")
    parser.add_argument("--max-items", type=int, default=8,
                        help="most findings one wave may carry (default 8); "
                             "this is a change-window policy, not a limit")
    args = parser.parse_args(argv)
    if args.max_items < 1:
        print("ERR --max-items must be at least 1", file=sys.stderr)
        return 2

    try:
        rows = read_findings(load_json(args.findings, "findings file"))
    except WaveError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not rows:
        print("OK 0 findings, nothing to schedule")
        return 0

    waves, blocked = build_plan(rows)
    print("FINDINGS %d in export" % len(rows))
    over = []
    for wave in WAVE_ORDER:
        items = waves[wave]
        if not items:
            continue
        assets = len({row["asset"] for row in items})
        services = len({row["service"] for row in items})
        print("WAVE %-6s %2d items, %2d assets, %2d services"
              % (wave, len(items), assets, services))
        groups = Counter((row["owner"], row["service"], row["fix"])
                         for row in items)
        (owner, service, fix), count = groups.most_common(1)[0]
        print("  top %s/%s %s x%d" % (owner, service, fix, count))
        if len(items) > args.max_items:
            over.append((wave, len(items)))

    if blocked:
        reasons = Counter(blocked)
        print("BLOCKED %d %s: %d no fix version, %d no owner"
              % (len(blocked), "finding" if len(blocked) == 1 else "findings",
                 reasons["no fix version"], reasons["no owner"]))

    for wave, count in over:
        print("FAIL wave %s: %d items over max %d"
              % (wave, count, args.max_items))
    if over:
        return 1

    scheduled = len(rows) - len(blocked)
    used = len([wave for wave in WAVE_ORDER if waves[wave]])
    print("OK %d waves, %d scheduled, max %d per wave"
          % (used, scheduled, args.max_items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
