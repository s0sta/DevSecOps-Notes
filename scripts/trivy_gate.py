#!/usr/bin/env python3
"""trivy_gate.py - fail a build on the Trivy findings that matter.

Reads the JSON that `trivy image -f json` writes, keeps the severities you
care about, subtracts an allowlist, and exits 1 if anything is left. It reads
the report only: it does not run Trivy, pull an image or change anything.

The fields used are the real Trivy schema:
    Results[].Target
    Results[].Vulnerabilities[].VulnerabilityID
    Results[].Vulnerabilities[].PkgName
    Results[].Vulnerabilities[].InstalledVersion
    Results[].Vulnerabilities[].FixedVersion
    Results[].Vulnerabilities[].Severity

Usage:
    trivy image -f json api:1.4.2 > trivy.json
    python3 trivy_gate.py trivy.json
    trivy image -f json api:1.4.2 | python3 trivy_gate.py -
    python3 trivy_gate.py trivy.json --allow-file .trivyignore
    python3 trivy_gate.py trivy.json --ignore-unfixed --severity CRITICAL

The allowlist file takes one vulnerability ID per line, # comments allowed,
the same shape as .trivyignore.

Exit codes: 0 clean, 1 blocking finding, 2 usage or read error.

CI:
    trivy image -f json "$IMAGE" | python3 trivy_gate.py -

By s0sta.com
"""
import argparse
import json
import sys
from pathlib import Path

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")


def severities(value):
    chosen = {s.strip().upper() for s in value.split(",") if s.strip()}
    bad = sorted(chosen - set(SEVERITIES))
    if not chosen or bad:
        raise argparse.ArgumentTypeError(
            "choose from %s" % ", ".join(SEVERITIES))
    return chosen


def allowlist(paths, inline):
    ids = {item.strip() for item in inline if item.strip()}
    for path in paths:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                ids.add(line.split()[0])
    return ids


def read_report(path):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    doc = json.loads(text)
    if not isinstance(doc, dict):
        raise ValueError("report is not a JSON object")
    if not any(k in doc for k in ("Results", "SchemaVersion", "ArtifactName")):
        raise ValueError("not a Trivy JSON report")
    return doc


def collect(doc, wanted, ignore_unfixed):
    found, below, unfixed = [], 0, 0
    seen = set()
    for result in doc.get("Results") or []:
        if not isinstance(result, dict):
            continue
        target = result.get("Target", "?")
        for vuln in result.get("Vulnerabilities") or []:
            if not isinstance(vuln, dict):
                continue
            severity = str(vuln.get("Severity", "")).upper()
            if severity not in wanted:
                below += 1
                continue
            fixed = vuln.get("FixedVersion") or ""
            if ignore_unfixed and not fixed:
                unfixed += 1
                continue
            key = (vuln.get("VulnerabilityID", "?"),
                   vuln.get("PkgName", "?"),
                   vuln.get("InstalledVersion", "?"))
            if key in seen:
                continue
            seen.add(key)
            found.append({
                "id": key[0], "pkg": key[1], "installed": key[2],
                "fixed": fixed, "severity": severity, "target": target,
            })
    return found, below, unfixed


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Gate a build on Trivy image scan JSON.")
    ap.add_argument("report", nargs="?", default="-", metavar="FILE",
                    help="Trivy JSON report, or - for stdin (default)")
    ap.add_argument("-s", "--severity", type=severities, default=severities("CRITICAL,HIGH"),
                    help="comma list, default CRITICAL,HIGH")
    ap.add_argument("-a", "--allow", action="append", default=[], metavar="ID",
                    help="allowlist one vulnerability ID (repeatable)")
    ap.add_argument("--allow-file", action="append", default=[], metavar="FILE",
                    help="file of IDs to allowlist, one per line")
    ap.add_argument("--ignore-unfixed", action="store_true",
                    help="skip findings with no FixedVersion")
    ap.add_argument("--show-allowlisted", action="store_true",
                    help="print the IDs that the allowlist removed")
    args = ap.parse_args(argv)

    try:
        allowed = allowlist(args.allow_file, args.allow)
        doc = read_report(args.report)
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    found, below, unfixed = collect(doc, args.severity, args.ignore_unfixed)
    blocking = [f for f in found if f["id"] not in allowed]
    skipped = [f for f in found if f["id"] in allowed]

    if args.show_allowlisted:
        for f in skipped:
            print("ALLOW  %s  %s  %s" % (f["id"], f["pkg"], f["severity"]))
    for f in blocking:
        fixed = f["fixed"] if f["fixed"] else "no fix"
        print("BLOCK  %-16s %-12s %-12s -> %-12s %s"
              % (f["id"], f["pkg"], f["installed"], fixed, f["severity"]))
    print("%d blocking, %d allowlisted, %d below threshold, %d unfixed"
          % (len(blocking), len(skipped), below, unfixed))
    if blocking:
        print("ALERT %d blocking, %d allowlisted" % (len(blocking), len(skipped)))
        print("FAIL %s" % (doc.get("ArtifactName") or args.report))
        return 1
    print("OK 0 blocking findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
