---
id: p744
title: "Map vulnerable packages onto live import paths"
slug: map-vulnerable-packages-onto-live-import-paths
sections: [devsecops]
topic: "Python scripts"
tags: [AppSec, SCA, VulnerabilityManagement, Python, CyberSecurity]
source: "LinkedIn post P744 · ASM series"
linkedin_date: 2031-06-29
design: code
script: reachability_map.py
---

# Map vulnerable packages onto live import paths

A CVSS 9.8 in a PDF library led the report for three sprints. No live module imported it: the service that used it was deleted a year earlier.

## Quick reference

The full script is at the end of this note: `reachability_map.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 reachability_map.py graph.json vuln.txt --entry app.main
```

**Example output**

```text
REACHABLE requests via app.api
UNREACHABLE paramiko
```

## Explained

### What it does

`reachability_map.py` reads an import graph export, a JSON object mapping each module to what it imports, plus a list of vulnerable import names. It walks from your entry points, marks every module it can reach, then reports each package as reachable with its path, or unreachable with the reason.

### What the screen shows

The panel walks from app.main and prints REACHABLE requests via app.api, then UNREACHABLE paramiko. The script adds the full path, the importer count and a summary; `--entry` names your roots.

### How to run it

`python3 reachability_map.py graph.json vuln.txt --entry app.main --entry` wsgi. Export the graph from your build tool or modulefinder and regenerate it on every merge. Exit 0 means nothing vulnerable is reachable, 1 means something is, 2 means bad input.

### The fix

Move the unreachable ones out of the weekly queue and keep the evidence line. Then delete the dead module, so the next graph needs no footnote.

### Prevention

Treat the graph as a build artefact: generate it in CI, diff it in review, and fail when a vulnerable package becomes reachable.

> **The honest caveat:** static imports miss importlib, plugins, template loaders and deserialisation, and a reachable import is not proof the vulnerable function runs.

> **The lesson:** reachability does not make a finding safe; it makes it later.

## In one line

> **Reachable is a maybe, not a no.** It moves a finding down the queue, not into the bin.

**Walk the imports**

```bash
python3 reachability_map.py g.json v.txt
```

## Script: reachability_map.py

Download: [scripts/reachability_map.py](../scripts/reachability_map.py)

```python
#!/usr/bin/env python3
"""Mark vulnerable packages that a live code path can actually import.

Reads an import graph export (JSON: module -> list of modules it imports) and a
list of vulnerable packages, walks the graph from the entry points, and reports
which packages are imported by a reachable module and which are not. For a
reachable package it prints the shortest path from an entry point.

    python3 reachability_map.py graph.json vuln_packages.txt
    python3 reachability_map.py graph.json vuln.txt --entry app.main --entry wsgi

Entry points default to modules that no other module imports. CI step, after
the graph export is regenerated (the build fails on exit 1):

    python3 reachability_map.py build/import_graph.json build/vuln.txt

The package list is import names, not distribution names: pyyaml is imported as
yaml, and python-dateutil as dateutil. A graph is static analysis. It cannot see
importlib, entry-point plugins, template loaders or code that is never executed.

Exit codes: 0 no vulnerable package is reachable, 1 at least one is, 2 bad
input.

By s0sta.com
"""
import argparse
import json
import sys


def die(msg):
    sys.stderr.write("reachability_map: %s\n" % msg)
    raise SystemExit(2)


def norm(name):
    return name.strip().lower().replace("-", "_")


def top(name):
    return norm(name).split(".")[0]


def imports_package(imported, wanted):
    name = norm(imported)
    return name == wanted or top(name) == wanted


def load_graph(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        die("cannot read graph %s: %s" % (path, exc))
    if isinstance(data, dict) and "modules" in data:
        data = data["modules"]
    if not isinstance(data, dict):
        die("graph must be a JSON object of module -> imports")
    graph = {}
    for module, imports in data.items():
        if not isinstance(imports, list):
            die("imports for %s must be a list" % module)
        clean = []
        for item in imports:
            if not isinstance(item, str):
                die("import for %s is not a string" % module)
            if item.strip():
                clean.append(item.strip())
        graph[str(module).strip()] = clean
    if not graph:
        die("graph %s has no modules" % path)
    return graph


def load_packages(path):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        die("cannot read package list %s: %s" % (path, exc))
    names = []
    if text.lstrip().startswith("["):
        try:
            data = json.loads(text)
        except ValueError as exc:
            die("package list looks like JSON but does not parse: %s" % exc)
        if not isinstance(data, list):
            die("JSON package list must be an array")
        for item in data:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict) and item.get("package"):
                names.append(str(item["package"]))
    else:
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                names.append(line)
    out = []
    for name in names:
        for sep in ("==", ">=", "<=", "~=", ">", "<", "="):
            if sep in name:
                name = name.split(sep, 1)[0]
        if name.strip():
            out.append(name.strip())
    if not out:
        die("no package names in %s" % path)
    seen, unique = set(), []
    for name in out:
        if norm(name) not in seen:
            seen.add(norm(name))
            unique.append(name)
    return unique


def walk(graph, entries):
    parent = {}
    queue = []
    for entry in entries:
        if entry not in graph:
            die("entry point %s is not in the graph" % entry)
        if entry not in parent:
            parent[entry] = None
            queue.append(entry)
    i = 0
    while i < len(queue):
        module = queue[i]
        i += 1
        for imported in graph.get(module, []):
            if imported not in graph:
                continue
            if imported not in parent:
                parent[imported] = module
                queue.append(imported)
    return parent


def path_to(parent, module):
    path = []
    while module is not None:
        path.append(module)
        module = parent[module]
    path.reverse()
    return " -> ".join(path)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Report vulnerable packages on a live import path.")
    ap.add_argument("graph", help="import graph export (JSON)")
    ap.add_argument("packages", help="vulnerable package list (txt or JSON)")
    ap.add_argument("--entry", action="append", default=[],
                    help="entry point module; repeatable")
    ap.add_argument("--json", action="store_true", help="print JSON, not text")
    args = ap.parse_args(argv)

    graph = load_graph(args.graph)
    packages = load_packages(args.packages)

    imported_by = {}
    for module, imports in graph.items():
        for imported in imports:
            imported_by.setdefault(imported, set()).add(module)

    if args.entry:
        entries = args.entry
        root = False
    else:
        entries = sorted(m for m in graph if m not in imported_by)
        root = True
        if not entries:
            # Every module is imported by another: a cycle. Assume the worst
            # rather than report real code as unreachable.
            entries = sorted(graph)
            print("NOTE no root modules; treating all %d as entry points"
                  % len(entries), file=sys.stderr)

    parent = walk(graph, entries)
    live = set(parent)

    rows = []
    for package in packages:
        wanted = norm(package)
        live_hits = sorted(m for m in live
                           if any(imports_package(i, wanted)
                                  for i in graph.get(m, [])))
        dead_hits = sorted(m for m in graph
                           if m not in live
                           and any(imports_package(i, wanted)
                                   for i in graph.get(m, [])))
        if live_hits:
            rows.append({"package": package, "state": "REACHABLE",
                         "path": path_to(parent, live_hits[0])
                                 + " -> " + norm(package),
                         "importers": live_hits})
        elif dead_hits:
            rows.append({"package": package, "state": "UNREACHABLE",
                         "path": "", "importers": dead_hits,
                         "reason": "imported only by modules off the live path"})
        else:
            rows.append({"package": package, "state": "UNREACHABLE",
                         "path": "", "importers": [],
                         "reason": "no import edge in the graph"})

    reachable = [r for r in rows if r["state"] == "REACHABLE"]

    if args.json:
        print(json.dumps({
            "entries": entries,
            "counts": {"modules": len(graph), "reachable_modules": len(live),
                       "packages": len(rows), "reachable_packages": len(reachable)},
            "packages": rows,
        }, indent=2))
        return 1 if reachable else 0

    if root:
        print("ENTRY %d roots: %s"
              % (len(entries), ", ".join(entries[:6])
                 + (" ..." if len(entries) > 6 else "")))
        print("NOTE no --entry given: every root counts as live, including "
              "scripts and tests")
    else:
        print("ENTRY %d given: %s" % (len(entries), ", ".join(entries)))
    for r in rows:
        if r["state"] == "REACHABLE":
            print("REACHABLE %-14s path %s (%d live importer%s)"
                  % (r["package"], r["path"], len(r["importers"]),
                     "" if len(r["importers"]) == 1 else "s"))
        elif r["importers"]:
            print("UNREACHABLE %-12s %s: %s"
                  % (r["package"], r["reason"], ", ".join(r["importers"])))
        else:
            print("UNREACHABLE %-12s %s" % (r["package"], r["reason"]))
    print("SUMMARY %d module%s, %d reachable, %d of %d vulnerable package%s "
          "reachable"
          % (len(graph), "" if len(graph) == 1 else "s", len(live),
             len(reachable), len(rows), "" if len(rows) == 1 else "s"))
    return 1 if reachable else 0


if __name__ == "__main__":
    sys.exit(main())
```
