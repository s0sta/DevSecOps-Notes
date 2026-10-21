---
id: p535
title: "An SBOM diff in Python"
slug: an-sbom-diff-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [SBOM, SupplyChain, Python, DevSecOps, CICD]
source: "LinkedIn post P535 · PythonSec series"
linkedin_date: 2030-02-26
design: code
script: sbom_diff.py
---

# An SBOM diff in Python

A base image update lands as a one-line change in the Dockerfile, and the image gains three packages and loses one. The tag says nothing about that, so compare the contents instead.

## Quick reference

The full script is at the end of this note: `sbom_diff.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 sbom_diff.py old.json new.json
```

**Example output**

```text
ADDED requests 2.31.0
CHANGED flask 2.2.5 -> 2.3.0
```

## Explained

### What it compares

The script loads two CycloneDX JSON files into a name-to-version map. Added components are names in the new file that are not in the old one. Removed components are the reverse. Changed components keep their name and get a new version, which is the line most people skip and the one a transitive bump usually shows up in.

### The exit code

The loops print added, removed and changed lines, each group sorted by name. When anything is different it exits 1; when the maps are identical it exits 0. That is the whole interface a pipeline needs: no parsing of prose, no grep for a warning, just a non-zero code that stops the promotion.

### Running it

`python3 sbom_diff.py old.json new.json`, where `old.json` is the SBOM stored beside the production image and `new.json` is the one from the build under test. Put it before the deploy step, not after, and keep the old file for as long as the rollback window.

> **The honest caveat:** the key is the component name, so a package that changes its name, or two packages that share one, will look like a removal and an addition rather than a change.

> **The lesson:** compare the inventory, not the tag.

## In one line

> **Diff the list, not the tag.** A tag is a name. The SBOM is what the name contains.

**Gate the build**

```bash
python3 sbom_diff.py old.json new.json
```

## Script: sbom_diff.py

Download: [scripts/sbom_diff.py](../scripts/sbom_diff.py)

```python
#!/usr/bin/env python3
"""Diff two CycloneDX JSON SBOMs and report what changed.

    python3 sbom_diff.py old.json new.json
    python3 sbom_diff.py prod.json candidate.json --ignore flask

Prints one line per component added, removed or version-changed, sorted by
name. Exits 1 when the inventory changed, 0 when the two SBOMs match, and 2
on a missing file, invalid JSON or an unexpected shape. Read-only.

CI/cron: python3 sbom_diff.py old.json new.json || exit 1
By s0sta.com
"""
import argparse
import json
import sys


def load(path):
    """Return {component name: version} from a CycloneDX JSON file."""
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
    found = {}
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise ValueError("%s: components[%d] is not an object" % (path, index))
        name = component.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("%s: components[%d] has no name" % (path, index))
        version = component.get("version", "?")
        if not isinstance(version, str):
            version = str(version)
        version = version or "?"
        if name in found and found[name] != version:
            raise ValueError("%s: duplicate component %s" % (path, name))
        found[name] = version
    return found


def main(argv=None):
    """Compare two SBOMs and return the process exit code."""
    parser = argparse.ArgumentParser(
        description="Diff two CycloneDX JSON SBOMs by component name.")
    parser.add_argument("old", help="baseline SBOM")
    parser.add_argument("new", help="candidate SBOM")
    parser.add_argument("--ignore", action="append", default=[], metavar="NAME",
                        help="component name to ignore (repeatable)")
    args = parser.parse_args(argv)
    ignore = set(args.ignore)
    try:
        old, new = load(args.old), load(args.new)
    except ValueError as exc:
        print("ERROR %s" % exc, file=sys.stderr)
        return 2

    old_names, new_names = set(old) - ignore, set(new) - ignore
    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)
    changed = sorted(name for name in old_names & new_names
                     if old[name] != new[name])

    for name in added:
        print("ADDED %s %s" % (name, new[name]))
    for name in removed:
        print("REMOVED %s %s" % (name, old[name]))
    for name in changed:
        print("CHANGED %s %s -> %s" % (name, old[name], new[name]))
    if not (added or removed or changed):
        print("OK no component changes")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
