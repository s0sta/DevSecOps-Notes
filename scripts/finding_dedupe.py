#!/usr/bin/env python3
"""Merge the same finding reported by several scanners into one record.

Reads two or more findings exports (JSON) and merges records that describe the
same thing: same asset and same CVE, or same asset and same normalised title
when there is no CVE. The merged record keeps the strongest evidence: the
highest CVSS, every scanner that saw it, and every package name reported. The
report then counts, per asset, how many reports arrived and how many findings
they actually were.

    python3 finding_dedupe.py nessus.json snyk.json trivy.json
    python3 finding_dedupe.py scan_*.json --max-dupes 2 --show 30

Nightly, after the scanner exports land:

    15 5 * * * python3 finding_dedupe.py exports/*.json --max-dupes 2

--max-dupes is a policy threshold, not a standard: it is how many duplicate
reports on a single asset you are willing to accept before the job fails.

Exit codes: 0 no asset is over the duplicate threshold, 1 at least one is,
2 bad input.

By s0sta.com
"""
import argparse
import json
import re
import sys

WORD = re.compile(r"[^a-z0-9]+")


def die(msg):
    sys.stderr.write("finding_dedupe: %s\n" % msg)
    raise SystemExit(2)


def norm_title(text):
    return WORD.sub(" ", (text or "").lower()).strip()


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        die("cannot read %s: %s" % (path, exc))
    if isinstance(data, dict):
        data = data.get("findings", data.get("results", []))
    if not isinstance(data, list):
        die("%s must contain a JSON list of findings" % path)
    out = []
    for i, f in enumerate(data):
        if not isinstance(f, dict):
            die("%s: finding %d is not an object" % (path, i))
        asset = str(f.get("asset", "") or "").strip()
        if not asset:
            die("%s: finding %d has no asset" % (path, i))
        cve = str(f.get("cve", "") or "").strip().upper()
        title = str(f.get("title", "") or "").strip()
        if not cve and not title:
            die("%s: finding %d has neither cve nor title" % (path, i))
        try:
            cvss = float(f.get("cvss", 0.0) or 0.0)
        except (TypeError, ValueError):
            die("%s: finding %d has a non-numeric cvss" % (path, i))
        out.append({
            "asset": asset,
            "cve": cve,
            "title": title,
            "scanner": str(f.get("scanner", "") or "unknown").strip(),
            "package": str(f.get("package", "") or "").strip(),
            "cvss": cvss,
            "source": path,
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Merge duplicate scanner findings into one record.")
    ap.add_argument("files", nargs="+", help="findings exports (JSON)")
    ap.add_argument("--max-dupes", type=int, default=2,
                    help="policy: duplicates per asset allowed (default 2)")
    ap.add_argument("--show", type=int, default=20,
                    help="merged records to print (default 20)")
    ap.add_argument("--json", action="store_true", help="print JSON, not text")
    args = ap.parse_args(argv)

    if args.max_dupes < 0:
        die("--max-dupes cannot be negative")
    if args.show < 1:
        die("--show must be at least 1")

    reports = []
    for path in args.files:
        reports.extend(load(path))
    if not reports:
        die("no findings in %d file(s)" % len(args.files))

    groups = {}
    for r in reports:
        if r["cve"]:
            key = (r["asset"].lower(), r["cve"])
        else:
            key = (r["asset"].lower(), "title:" + norm_title(r["title"]))
        if key not in groups:
            groups[key] = {"asset": r["asset"], "cve": r["cve"],
                           "title": r["title"], "cvss": r["cvss"],
                           "scanners": set(), "packages": set(),
                           "sources": set(), "reports": 0}
        g = groups[key]
        g["reports"] += 1
        g["scanners"].add(r["scanner"])
        g["sources"].add(r["source"])
        if r["package"]:
            g["packages"].add(r["package"])
        if r["cvss"] > g["cvss"]:
            g["cvss"] = r["cvss"]
        if not g["title"] and r["title"]:
            g["title"] = r["title"]

    per_asset = {}
    for g in groups.values():
        a = per_asset.setdefault(g["asset"], {"reported": 0, "unique": 0})
        a["reported"] += g["reports"]
        a["unique"] += 1

    duplicate_total = sum(a["reported"] - a["unique"] for a in per_asset.values())
    over = sorted(n for n, a in per_asset.items()
                  if a["reported"] - a["unique"] > args.max_dupes)

    merged = sorted(groups.values(),
                    key=lambda g: (-g["reports"], -g["cvss"], g["asset"],
                                   g["cve"]))

    if args.json:
        print(json.dumps({
            "counts": {"files": len(args.files), "reports": len(reports),
                       "unique": len(groups), "duplicates": duplicate_total},
            "policy": {"max_dupes": args.max_dupes},
            "over_threshold": [
                {"asset": n,
                 "duplicates": per_asset[n]["reported"] - per_asset[n]["unique"]}
                for n in over],
            "assets": [{"asset": n, "reported": a["reported"],
                        "unique": a["unique"],
                        "duplicates": a["reported"] - a["unique"]}
                       for n, a in sorted(per_asset.items())],
            "merged": [dict(g, scanners=sorted(g["scanners"]),
                            packages=sorted(g["packages"]),
                            sources=sorted(g["sources"]))
                       for g in merged[:args.show]],
        }, indent=2))
        return 1 if over else 0

    print("MERGED %d report%s from %d file%s into %d finding%s"
          % (len(reports), "" if len(reports) == 1 else "s",
             len(args.files), "" if len(args.files) == 1 else "s",
             len(groups), "" if len(groups) == 1 else "s"))
    for g in merged[:args.show]:
        label = g["cve"] or g["title"][:40]
        packages = ",".join(sorted(g["packages"])) or "-"
        print("%-10s %-16s %d report%s  scanners %-24s cvss %4.1f  %s"
              % (g["asset"], label, g["reports"],
                 "" if g["reports"] == 1 else "s",
                 ",".join(sorted(g["scanners"]))[:24], g["cvss"], packages))
    for name, a in sorted(per_asset.items(), key=lambda kv: -kv[1]["reported"]):
        dupes = a["reported"] - a["unique"]
        print("ASSET %-10s %3d reported, %3d unique, %3d duplicates"
              % (name, a["reported"], a["unique"], dupes))
    print("SUMMARY %d file%s, %d report%s, %d unique, %d duplicate%s, "
          "%d asset(s) over the policy limit of %d"
          % (len(args.files), "" if len(args.files) == 1 else "s",
             len(reports), "" if len(reports) == 1 else "s",
             len(groups), duplicate_total,
             "" if duplicate_total == 1 else "s",
             len(over), args.max_dupes))
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
