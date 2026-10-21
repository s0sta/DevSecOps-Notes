---
id: p765
title: "Map the finding to the control"
slug: map-the-finding-to-the-control
sections: [devsecops]
topic: "Python scripts"
tags: [Python, GRC, SOC2, Compliance, CyberSecurity]
source: "LinkedIn post P765 · ASM series"
linkedin_date: 2031-08-17
design: code
script: control_map.py
---

# Map the finding to the control

The auditor asks which control covers the backup finding. The answer is a category name and a hope, and the finding goes into the pack without an id.

## Quick reference

The full script is at the end of this note: `control_map.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 control_map.py findings.json soc2.json
```

**Example output**

```text
CONTROL MAP 7/9 categories (SOC 2)
UNMAPPED 5 findings, 2 high
```

## Explained

### What it does

`control_map.py` reads the findings and a framework file that maps each category to SOC 2 or ISO control ids. It prints the categories covered, the control ids in the framework, and every finding whose category has no control. Exit 1 when an unmapped finding is at or above `--fail-on`, high by default.

### On the screen

CONTROL MAP 7/9 categories (SOC 2), then UNMAPPED 5 findings, 2 high. The two categories are saas_review and backup_policy; both high findings have no control id.

### How to run it

`python3 control_map.py findings.json soc2.json`, weekly before the audit sync. Exit 0 is every high finding mapped, 1 is at least one without a control, 2 is a bad file; the high line is policy.

### The fix

Map every scanner category once, in a versioned file reviewed with the control owner. Every finding then inherits a control, and the audit query becomes a join instead of a search.

### Prevention

Fail the weekly job on a high unmapped finding. A new scanner category cannot ship without a mapping, and the mapping lives in git beside the policy.

> **The honest caveat:** a mapped control is not a working control. The map says where the finding belongs; the evidence is a separate packet.

> **The lesson:** a finding without a control is a story the auditor cannot file.

## In one line

> **A finding without a control is a story.** A control id is what turns a finding into an audit row.

**Map it first**

```bash
python3 control_map.py f.json soc2.json
```

## Script: control_map.py

Download: [scripts/control_map.py](../scripts/control_map.py)

```python
#!/usr/bin/env python3
"""control_map.py - map every finding category to a control id.

Reads a findings export and a control framework file and answers two audit
questions: how much of the finding set has a control, and which findings have
none. A finding with no control cannot be reported against SOC 2 or ISO 27001
without a story, and a story is not evidence.

Findings JSON is a list of objects:

    [{"id": "F-101", "category": "saas_review", "severity": "high",
      "asset": "notion"}]

Framework JSON maps each finding category to one or more control ids:

    {"framework": "SOC 2", "version": "2026",
     "controls": {"patch_management": ["CC7.1"],
                  "access_review": ["CC6.1", "CC6.2"]}}

Categories are the vocabulary your scanners emit. Keep them stable: a renamed
category silently becomes an unmapped finding. The exit code fails only for
findings at or above --fail-on, because an unmapped low finding is a backlog
item, while an unmapped high finding is an audit gap.

Usage:
    python3 control_map.py findings.json soc2.json
    python3 control_map.py findings.json soc2.json --fail-on critical
    python3 control_map.py findings.json soc2.json --show 20

Cron (weekly, Monday 06:30, before the audit sync):
    30 6 * * 1 python3 /opt/s0sta/control_map.py /var/lib/s0sta/findings.json /etc/s0sta/soc2.json

CI (fail when a high finding has no control):
    python3 control_map.py findings.json soc2.json || exit 1

Exit codes: 0 no unmapped finding at or above --fail-on, 1 at least one,
2 usage or a findings or framework file that is missing, unreadable, invalid
or inconsistent.

Read-only: reads the two files and prints. It writes nothing and makes no
network call.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys

RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class InputError(Exception):
    """A file that cannot be used for the mapping."""


def load_findings(path):
    """Read findings. Return a list of (id, category, severity)."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, list):
        raise InputError("%s must contain a JSON list of findings" % path)

    rows = []
    seen = set()
    for number, item in enumerate(doc, 1):
        if not isinstance(item, dict):
            raise InputError("%s: finding %d is not an object" % (path, number))
        finding_id = item.get("id")
        if not isinstance(finding_id, str) or not finding_id.strip():
            raise InputError("%s: finding %d has no id" % (path, number))
        finding_id = finding_id.strip()
        if finding_id in seen:
            raise InputError("%s: duplicate finding id %s" % (path, finding_id))
        seen.add(finding_id)
        category = item.get("category")
        if not isinstance(category, str) or not category.strip():
            raise InputError("%s: %s has no category" % (path, finding_id))
        severity = item.get("severity")
        if severity not in RANK:
            raise InputError("%s: %s has an unknown severity %r"
                             % (path, finding_id, severity))
        rows.append((finding_id, category.strip(), severity))
    return rows


def load_framework(path):
    """Read the framework. Return (name, {category: [control ids]})."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, dict):
        raise InputError("%s must contain a JSON object" % path)
    name = doc.get("framework")
    if not isinstance(name, str) or not name.strip():
        raise InputError("%s has no framework name" % path)
    controls = doc.get("controls")
    if not isinstance(controls, dict):
        raise InputError("%s has no controls object" % path)

    mapping = {}
    for category, ids in controls.items():
        if not isinstance(category, str) or not category.strip():
            raise InputError("%s has an empty control category" % path)
        if not isinstance(ids, list) or not ids:
            raise InputError("%s: category %s has no control ids"
                             % (path, category))
        clean = []
        for control in ids:
            if not isinstance(control, str) or not control.strip():
                raise InputError("%s: category %s has an empty control id"
                                 % (path, category))
            control = control.strip()
            if control not in clean:
                clean.append(control)
        mapping[category.strip()] = clean
    return name.strip(), mapping


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Map finding categories to control framework ids.")
    parser.add_argument("findings", help="JSON list of findings")
    parser.add_argument("framework", help="JSON framework with category to control ids")
    parser.add_argument("--fail-on", choices=("critical", "high", "medium", "low"),
                        default="high",
                        help="severity at which an unmapped finding fails the "
                             "job (default high)")
    parser.add_argument("--show", type=int, default=10,
                        help="unmapped findings to list (default 10)")
    args = parser.parse_args(argv)
    if args.show < 0:
        parser.error("--show must be zero or more")

    try:
        findings = load_findings(args.findings)
        framework, mapping = load_framework(args.framework)
    except InputError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    categories = {category for _, category, _ in findings}
    mapped = categories & set(mapping)
    controls = {control for ids in mapping.values() for control in ids}
    unmapped = [row for row in findings if row[1] not in mapping]
    high_unmapped = [row for row in unmapped
                     if RANK[row[2]] >= RANK[args.fail_on]]

    print("CONTROL MAP %d/%d categories (%s)"
          % (len(mapped), len(categories), framework))
    print("UNMAPPED %d findings, %d %s"
          % (len(unmapped), len(high_unmapped), args.fail_on))
    if unmapped:
        print("CATEGORIES " + ", ".join(sorted({row[1] for row in unmapped})))
        for finding_id, category, severity in unmapped[:args.show]:
            print("  %s %s %s" % (finding_id, category, severity))
        if len(unmapped) > args.show:
            print("  ... %d more" % (len(unmapped) - args.show))
    print("CONTROLS %d ids across %d categories" % (len(controls), len(mapping)))

    if high_unmapped:
        print("FAIL %d finding%s at or above %s without a control"
              % (len(high_unmapped), "" if len(high_unmapped) == 1 else "s",
                 args.fail_on))
        return 1
    print("OK every finding at or above %s has a control" % args.fail_on)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
