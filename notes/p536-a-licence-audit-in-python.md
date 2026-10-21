---
id: p536
title: "A licence audit in Python"
slug: a-licence-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [SBOM, OpenSource, DevSecOps, Python, SupplyChain]
source: "LinkedIn post P536 · PythonSec series"
linkedin_date: 2030-02-28
design: code
script: license_audit.py
---

# A licence audit in Python

A legal review asks for every licence in the product, and the answer is spread across three package managers and a container base image. An SBOM already has the licences; the missing part is the decision.

## Quick reference

The full script is at the end of this note: `license_audit.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 license_audit.py --allow MIT,BSD-3-Clause --deny GPL-3.0 licenses.json
```

**Example output**

```text
FINDING libfoo GPL-3.0
FINDING mystery NO-LICENCE
```

## Explained

### The lists

The script reads a CycloneDX file and takes two comma-separated sets: what the organisation allows and what it forbids. A licence on the deny list always fails, even if someone also put it on the allow list. When an allow list is present, anything outside it fails too, which is how most policies actually read.

### The findings

Each component contributes its licence IDs. A component with no licence entry gets NO-LICENCE, because missing metadata is a question, not a permission. Findings print one per line with the component name and the licence, then the process exits 1. A clean file exits 0.

### The output

`python3 license_audit.py --allow MIT,BSD-3-Clause --deny GPL-3.0 licenses.json` prints libfoo GPL-3.0 and mystery NO-LICENCE in the example, which is exactly the pair a reviewer needs to see. Wire it into the build after the SBOM is generated and before the image is pushed.

> **The honest caveat:** it compares the identifier in the SBOM, so a package that declares Apache-2.0 in its metadata but ships a different file is invisible to this check.

> **The lesson:** an allow list is a policy, and a policy needs an exit code.

## In one line

> **A licence is a decision.** The file records it. The gate enforces it.

**Audit the sbom:** `license_audit.py sbom.json --allow` MIT

## Script: license_audit.py

Download: [scripts/license_audit.py](../scripts/license_audit.py)

```python
#!/usr/bin/env python3
"""Audit the licences in a CycloneDX SBOM against allow and deny lists.

    python3 license_audit.py sbom.json --allow MIT,Apache-2.0
    python3 license_audit.py sbom.json --deny GPL-3.0,AGPL-3.0
    python3 license_audit.py sbom.json --allow MIT --deny GPL-3.0

A component with no licence entry is reported as NO-LICENCE. A licence on
the deny list always fails, even when it is also on the allow list. Licence
IDs are compared case-insensitively; an SPDX expression is treated as one
string. Exits 1 on a disallowed or unknown licence, 0 when clean, and 2 on a
missing file, invalid JSON or an unexpected shape. Read-only.

CI/cron: python3 license_audit.py sbom.json --allow MIT,Apache-2.0 || exit 1
By s0sta.com
"""
import argparse
import json
import sys


def parse_list(value):
    """Turn a comma-separated option into a set of lower-case names."""
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def load(path):
    """Return [(component name, [licence, ...]), ...] from an SBOM."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise ValueError("invalid JSON in %s: %s" % (path, exc))
    if not isinstance(data, dict):
        raise ValueError("%s: top level must be a JSON object" % path)
    components = data.get("components")
    if not isinstance(components, list):
        raise ValueError("%s: no components list" % path)
    found = []
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise ValueError("%s: components[%d] is not an object" % (path, index))
        name = component.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("%s: components[%d] has no name" % (path, index))
        entries = component.get("licenses", [])
        if not isinstance(entries, list):
            raise ValueError("%s: %s has a non-list licenses field" % (path, name))
        licences = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            licence = entry.get("license")
            value = None
            if isinstance(licence, dict):
                value = licence.get("id") or licence.get("name")
            elif isinstance(entry.get("expression"), str):
                value = entry["expression"]
            if isinstance(value, str) and value.strip():
                licences.append(value.strip())
        found.append((name, licences))
    return found


def main(argv=None):
    """Audit the SBOM and return the process exit code."""
    parser = argparse.ArgumentParser(
        description="Audit CycloneDX SBOM licences against allow and deny lists.")
    parser.add_argument("sbom", help="CycloneDX JSON SBOM to audit")
    parser.add_argument("--allow", default="", metavar="IDS",
                        help="comma-separated licences to allow")
    parser.add_argument("--deny", default="", metavar="IDS",
                        help="comma-separated licences to deny")
    args = parser.parse_args(argv)
    allow, deny = parse_list(args.allow), parse_list(args.deny)
    try:
        components = load(args.sbom)
    except ValueError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    findings = []
    for name, licences in components:
        if not licences:
            findings.append((name, "NO-LICENCE"))
            continue
        for licence in licences:
            key = licence.lower()
            if key in deny or (allow and key not in allow):
                findings.append((name, licence))
    findings = sorted(set(findings))
    if not findings:
        print("OK all licences allowed")
        return 0
    for name, licence in findings:
        print("FINDING %s %s" % (name, licence))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
