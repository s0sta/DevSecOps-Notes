#!/usr/bin/env python3
"""Score each asset, then rank findings by asset score x CVSS.

Reads an asset export (JSON) and a findings export (JSON). Scores every asset
from four factors, prints the factors next to the score, then ranks the
findings by asset score times CVSS base score.

    python3 exposure_score.py assets.json findings.json
    python3 exposure_score.py cmdb.json findings.json --min-score 70

The asset export is an object keyed by asset name, each with internet_facing
and auth_required booleans, data (high, medium, low) and complexity (low,
medium, high). A list of objects with an asset field also works.

Weekly, after the CMDB export:

    0 6 * * 1 python3 exposure_score.py cmdb.json findings.json --min-score 60

The weights below are a policy choice, not an industry standard. Change them
in one place, write down why, and review them quarterly. The --min-score and
--cvss-floor defaults are policy lines too.

Exit codes: 0 no finding at or above the CVSS floor sits on an asset at or
above the score line, 1 at least one does, 2 bad input.

By s0sta.com
"""
import argparse
import json
import sys

WEIGHTS = {
    "internet_facing": 40,
    "internal": 10,
    "auth_required": -15,
    "data_high": 30,
    "data_medium": 18,
    "data_low": 6,
    "complexity_low": 30,
    "complexity_medium": 15,
    "complexity_high": 5,
}
DATA = ("high", "medium", "low")
COMPLEXITY = ("low", "medium", "high")


def die(msg):
    sys.stderr.write("exposure_score: %s\n" % msg)
    raise SystemExit(2)


def as_bool(value, field, name):
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "yes", "1"):
        return True
    if isinstance(value, str) and value.strip().lower() in ("false", "no", "0"):
        return False
    die("%s: %s must be true or false" % (name, field))


def load_assets(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        die("cannot read assets %s: %s" % (path, exc))
    if isinstance(data, dict) and "assets" in data:
        data = data["assets"]
    items = []
    if isinstance(data, dict):
        for name, spec in data.items():
            if not isinstance(spec, dict):
                die("asset %s must be an object" % name)
            row = dict(spec)
            row["asset"] = str(name)
            items.append(row)
    elif isinstance(data, list):
        for i, spec in enumerate(data):
            if not isinstance(spec, dict):
                die("asset %d is not an object" % i)
            row = dict(spec)
            row["asset"] = str(row.get("asset") or row.get("name") or "")
            items.append(row)
    else:
        die("assets must be a JSON object or list")
    out = {}
    for row in items:
        name = row["asset"].strip()
        if not name:
            die("an asset has no name")
        data_class = str(row.get("data", "")).strip().lower()
        complexity = str(row.get("complexity", "")).strip().lower()
        if data_class not in DATA:
            die("%s: data must be one of %s" % (name, ", ".join(DATA)))
        if complexity not in COMPLEXITY:
            die("%s: complexity must be one of %s"
                % (name, ", ".join(COMPLEXITY)))
        out[name] = {
            "asset": name,
            "internet_facing": as_bool(row.get("internet_facing"), "internet_facing", name),
            "auth_required": as_bool(row.get("auth_required"), "auth_required", name),
            "data": data_class,
            "complexity": complexity,
        }
    if not out:
        die("no assets in %s" % path)
    return out


def load_findings(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        die("cannot read findings %s: %s" % (path, exc))
    if isinstance(data, dict):
        data = data.get("findings", data.get("results", []))
    if not isinstance(data, list):
        die("findings must be a JSON list")
    out = []
    for i, f in enumerate(data):
        if not isinstance(f, dict):
            die("finding %d is not an object" % i)
        cve = str(f.get("cve", "")).strip().upper()
        if not cve.startswith("CVE-"):
            die("finding %d has no cve field" % i)
        try:
            cvss = float(f.get("cvss", 0.0))
        except (TypeError, ValueError):
            die("finding %d (%s) has a non-numeric cvss" % (i, cve))
        out.append({
            "cve": cve,
            "cvss": cvss,
            "asset": str(f.get("asset", "") or "").strip(),
            "package": str(f.get("package", "") or "-"),
        })
    return out


def score_asset(spec):
    exposure = WEIGHTS["internet_facing"] if spec["internet_facing"] \
        else WEIGHTS["internal"]
    auth = WEIGHTS["auth_required"] if spec["auth_required"] else 0
    exposure = max(0, exposure + auth)
    data = WEIGHTS["data_" + spec["data"]]
    complexity = WEIGHTS["complexity_" + spec["complexity"]]
    total = max(0, min(100, exposure + data + complexity))
    return total, {"exposure": exposure, "data": data,
                   "complexity": complexity}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Score assets and rank findings by score x CVSS.")
    ap.add_argument("assets", help="asset export (JSON)")
    ap.add_argument("findings", help="findings export (JSON)")
    ap.add_argument("--min-score", type=int, default=60,
                    help="policy line for a high-score asset (default 60)")
    ap.add_argument("--cvss-floor", type=float, default=7.0,
                    help="policy line for a high CVSS (default 7.0)")
    ap.add_argument("--json", action="store_true", help="print JSON, not text")
    args = ap.parse_args(argv)

    if not 0 <= args.min_score <= 100:
        die("--min-score must be between 0 and 100")
    if not 0.0 <= args.cvss_floor <= 10.0:
        die("--cvss-floor must be between 0 and 10")

    assets = load_assets(args.assets)
    findings = load_findings(args.findings)

    scored = {}
    unknown = set()
    for name, spec in assets.items():
        total, parts = score_asset(spec)
        scored[name] = {"spec": spec, "score": total, "parts": parts}

    rows = []
    for f in findings:
        hit = scored.get(f["asset"])
        if hit is None:
            unknown.add(f["asset"] or "-")
            rows.append({"cve": f["cve"], "asset": f["asset"], "cvss": f["cvss"],
                         "package": f["package"], "score": 0, "rank": 0.0,
                         "known": False})
            continue
        rows.append({"cve": f["cve"], "asset": f["asset"], "cvss": f["cvss"],
                     "package": f["package"], "score": hit["score"],
                     "rank": round(hit["score"] * f["cvss"], 1),
                     "known": True})
    rows.sort(key=lambda r: (-r["rank"], -r["cvss"], r["cve"]))

    flagged = [r for r in rows if r["known"] and r["cvss"] >= args.cvss_floor
               and r["score"] >= args.min_score]

    if args.json:
        print(json.dumps({
            "policy": {"min_score": args.min_score,
                       "cvss_floor": args.cvss_floor},
            "weights": WEIGHTS,
            "assets": [{"asset": n, "score": s["score"], "parts": s["parts"],
                        "spec": s["spec"]} for n, s in sorted(scored.items())],
            "ranked": rows,
            "flagged": len(flagged),
            "unknown_assets": sorted(unknown),
        }, indent=2))
        return 1 if flagged else 0

    for name, s in sorted(scored.items(), key=lambda kv: -kv[1]["score"]):
        spec, parts = s["spec"], s["parts"]
        print("ASSET %-10s score %3d  exposure %+d (internet %s, auth %s)  "
              "data %+d (%s)  complexity %+d (%s)"
              % (name, s["score"], parts["exposure"],
                 "yes" if spec["internet_facing"] else "no",
                 "yes" if spec["auth_required"] else "no",
                 parts["data"], spec["data"], parts["complexity"],
                 spec["complexity"]))
    print("POLICY min-score %d, cvss-floor %.1f"
          % (args.min_score, args.cvss_floor))
    print("RANK %d findings by asset score x CVSS" % len(rows))
    for r in rows:
        print("RANK %6.1f  %-16s cvss %4.1f  %-10s score %3d  %s"
              % (r["rank"], r["cve"], r["cvss"], r["asset"], r["score"],
                 r["package"]))
    for name in sorted(unknown):
        print("NOTE asset %s is not in the asset export; scored 0" % name)
    print("SUMMARY %d assets, %d findings, %d flagged high on a high-score asset"
          % (len(scored), len(rows), len(flagged)))
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
