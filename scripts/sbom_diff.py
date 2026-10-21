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
