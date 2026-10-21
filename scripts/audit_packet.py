#!/usr/bin/env python3
"""audit_packet.py - assemble a read-only audit evidence packet.

Reads a directory of evidence files plus the findings, scans and remediation
records that reference them, and prints a packet to stdout:

  - a manifest with the size and SHA-256 of every evidence file, plus one
    bundle hash over the sorted manifest lines;
  - a per-control evidence index, built from successful scans and from
    remediation records;
  - a gaps section: referenced files that are missing, controls with no
    evidence, orphan files nobody references, and high findings still open
    without evidence.

Findings JSON:

    [{"id": "F-1", "control": "CC7.1", "severity": "high", "status": "open"}]

Scans JSON:

    [{"date": "2026-10-12", "tool": "trivy", "target": "web-01",
      "control": "CC7.1", "status": "ok", "evidence": "trivy-web-01.json"}]

Remediation JSON:

    [{"finding": "F-3", "control": "CC6.1", "closed": "2026-10-14",
      "evidence": "patch-web-03.txt"}]

Evidence names are file names inside the evidence directory, never paths. A
symlink is not followed: it is reported as a gap, because evidence that can
point outside the packet is not evidence. Only a successful scan is indexed;
a failed scan is an attempt.

The packet is printed, never written. Redirect stdout if you want a file, then
sign or archive it. The script opens the evidence files read-only.

Usage:
    python3 audit_packet.py evidence/ -f findings.json -s scans.json -r remediation.json
    python3 audit_packet.py evidence/ -f findings.json -s scans.json -r remediation.json --fail-on critical

Cron (monthly, on the first, before the control review):
    0 5 1 * * python3 /opt/s0sta/audit_packet.py /var/lib/s0sta/evidence -f /var/lib/s0sta/findings.json -s /var/lib/s0sta/scans.json -r /var/lib/s0sta/remediation.json

Exit codes: 0 the packet is complete for every record, 1 a referenced file is
missing or unreadable, a symlink or non-file sits in the evidence directory,
or a finding at or above --fail-on is open without evidence, 2 usage or an
input that is missing, unreadable, invalid or inconsistent.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import stat
import sys

RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
CHUNK = 1024 * 1024


class InputError(Exception):
    """An input that cannot be assembled into a packet."""


def parse_day(text, label):
    """Return a date from an ISO string, or raise InputError."""
    if not isinstance(text, str):
        raise InputError("%s is not an ISO date" % label)
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        raise InputError("%s is not an ISO date: %s" % (label, text))


def check_evidence_name(name, label):
    """Accept only a plain file name inside the evidence directory."""
    if not isinstance(name, str) or not name.strip():
        raise InputError("%s has no evidence file name" % label)
    name = name.strip()
    if (name in (".", "..") or os.path.isabs(name)
            or os.path.basename(name) != name
            or (os.altsep and os.altsep in name)):
        raise InputError("%s evidence must be a file name, not a path: %s"
                         % (label, name))
    return name


def load_json(path, kind):
    """Read one JSON document with a clear error."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise InputError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise InputError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, list):
        raise InputError("%s must contain a JSON list of %s" % (path, kind))
    return doc


def load_findings(path):
    """Return validated findings records."""
    rows = []
    seen = set()
    for number, item in enumerate(load_json(path, "findings"), 1):
        if not isinstance(item, dict):
            raise InputError("%s: finding %d is not an object" % (path, number))
        finding_id = item.get("id")
        if not isinstance(finding_id, str) or not finding_id.strip():
            raise InputError("%s: finding %d has no id" % (path, number))
        finding_id = finding_id.strip()
        if finding_id in seen:
            raise InputError("%s: duplicate finding id %s" % (path, finding_id))
        seen.add(finding_id)
        control = item.get("control")
        if not isinstance(control, str) or not control.strip():
            raise InputError("%s: %s has no control" % (path, finding_id))
        severity = item.get("severity")
        if severity not in RANK:
            raise InputError("%s: %s has an unknown severity %r"
                             % (path, finding_id, severity))
        status = item.get("status")
        if status not in ("open", "fixed"):
            raise InputError("%s: %s has an unknown status %r"
                             % (path, finding_id, status))
        rows.append({"id": finding_id, "control": control.strip(),
                     "severity": severity, "status": status})
    return rows


def load_scans(path):
    """Return validated scan records."""
    rows = []
    for number, item in enumerate(load_json(path, "scans"), 1):
        if not isinstance(item, dict):
            raise InputError("%s: scan %d is not an object" % (path, number))
        for key in ("tool", "target", "control"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise InputError("%s: scan %d has no %s" % (path, number, key))
        parse_day(item.get("date"), "%s: scan %d date" % (path, number))
        status = item.get("status")
        if status not in ("ok", "failed"):
            raise InputError("%s: scan %d has an unknown status %r"
                             % (path, number, status))
        evidence = None
        if item.get("evidence") is not None:
            evidence = check_evidence_name(item["evidence"],
                                           "%s: scan %d" % (path, number))
        rows.append({"tool": item["tool"].strip(), "target": item["target"].strip(),
                     "control": item["control"].strip(), "status": status,
                     "evidence": evidence})
    return rows


def load_remediation(path):
    """Return validated remediation records."""
    rows = []
    seen = set()
    for number, item in enumerate(load_json(path, "remediation records"), 1):
        if not isinstance(item, dict):
            raise InputError("%s: record %d is not an object" % (path, number))
        for key in ("finding", "control"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise InputError("%s: record %d has no %s" % (path, number, key))
        finding = item["finding"].strip()
        if finding in seen:
            raise InputError("%s: duplicate remediation for %s" % (path, finding))
        seen.add(finding)
        parse_day(item.get("closed"), "%s: record %d closed" % (path, number))
        evidence = None
        if item.get("evidence") is not None:
            evidence = check_evidence_name(item["evidence"],
                                           "%s: record %d" % (path, number))
        rows.append({"finding": finding, "control": item["control"].strip(),
                     "evidence": evidence})
    return rows


def sha256_file(path):
    """Return the hex digest and size of one file."""
    digest = hashlib.sha256()
    size = 0
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def read_evidence(root):
    """Hash the directory. Return (files dict, problems list)."""
    files = {}
    problems = []
    try:
        names = sorted(os.listdir(root))
    except OSError as exc:
        raise InputError("cannot list %s: %s" % (root, exc))
    for name in names:
        path = os.path.join(root, name)
        try:
            info = os.lstat(path)
        except OSError as exc:
            problems.append("%s: %s" % (name, exc))
            continue
        if stat.S_ISLNK(info.st_mode):
            problems.append("%s: symlink not followed" % name)
            continue
        if not stat.S_ISREG(info.st_mode):
            problems.append("%s: not a regular file" % name)
            continue
        try:
            digest, size = sha256_file(path)
        except OSError as exc:
            problems.append("%s: %s" % (name, exc))
            continue
        files[name] = {"sha256": digest, "size": size}
    return files, problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Assemble a read-only audit evidence packet from findings, "
                    "scans and remediation records.")
    parser.add_argument("evidence", help="directory of evidence files")
    parser.add_argument("-f", "--findings", required=True,
                        help="findings JSON export")
    parser.add_argument("-s", "--scans", required=True,
                        help="scan records JSON export")
    parser.add_argument("-r", "--remediation", required=True,
                        help="remediation records JSON export")
    parser.add_argument("--fail-on", choices=("critical", "high", "medium", "low"),
                        default="high",
                        help="severity at which an open finding without "
                             "evidence fails the packet (default high)")
    args = parser.parse_args(argv)

    try:
        root = os.path.realpath(args.evidence)
        if not os.path.isdir(root):
            raise InputError("not a directory: %s" % args.evidence)
        findings = load_findings(args.findings)
        scans = load_scans(args.scans)
        remediation = load_remediation(args.remediation)
        files, problems = read_evidence(root)
    except InputError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    referenced = set()
    for scan in scans:
        if scan["evidence"]:
            referenced.add(scan["evidence"])
    for record in remediation:
        if record["evidence"]:
            referenced.add(record["evidence"])
    present = set(files)
    missing = sorted(referenced - present)
    orphans = sorted(present - referenced)

    print("PACKET %d files, %d referenced" % (len(files), len(referenced & present)))
    bundle = hashlib.sha256()
    for name in sorted(files):
        bundle.update(("%s  %s\n" % (files[name]["sha256"], name)).encode("utf-8"))
    print("MANIFEST %d files, %d bytes, bundle %s" % (
        len(files), sum(row["size"] for row in files.values()),
        bundle.hexdigest() if files else "-"))
    for name in sorted(files):
        print("FILE %s %9d %s" % (files[name]["sha256"],
                                  files[name]["size"], name))

    controls = sorted({finding["control"] for finding in findings})
    for control in controls:
        names = set()
        for scan in scans:
            if (scan["control"] == control and scan["status"] == "ok"
                    and scan["evidence"]):
                names.add(scan["evidence"])
        for record in remediation:
            if record["control"] == control and record["evidence"]:
                names.add(record["evidence"])
        if not names:
            print("EVIDENCE %s: none" % control)
            continue
        shown = ", ".join(
            name + ("" if name in present else " (missing)")
            for name in sorted(names))
        print("EVIDENCE %s: %s" % (control, shown))

    open_high = [finding for finding in findings
                 if finding["status"] == "open"
                 and RANK[finding["severity"]] >= RANK[args.fail_on]]
    with_evidence = {record["finding"] for record in remediation
                     if record["evidence"] in present}
    open_gap = [finding for finding in open_high
                if finding["id"] not in with_evidence]
    no_evidence = []
    for control in controls:
        covered = any(scan["control"] == control and scan["status"] == "ok"
                      and scan["evidence"] in present for scan in scans)
        covered = covered or any(record["control"] == control
                                 and record["evidence"] in present
                                 for record in remediation)
        if not covered:
            no_evidence.append(control)

    print("GAPS %d missing, %d %s open"
          % (len(missing), len(open_gap), args.fail_on))
    for name in missing:
        print("MISSING %s" % name)
    if no_evidence:
        print("NO EVIDENCE " + ", ".join(no_evidence))
    if orphans:
        print("ORPHAN " + ", ".join(orphans))
    for problem in problems:
        print("PROBLEM %s" % problem)

    if not files:
        print("FAIL packet has no evidence files")
        return 1
    if missing or open_gap or problems:
        parts = []
        if missing:
            parts.append("%d missing file%s"
                         % (len(missing), "" if len(missing) == 1 else "s"))
        if open_gap:
            parts.append("%d finding%s without evidence"
                         % (len(open_gap), "" if len(open_gap) == 1 else "s"))
        if problems:
            parts.append("%d evidence problem%s"
                         % (len(problems), "" if len(problems) == 1 else "s"))
        print("FAIL " + ", ".join(parts))
        return 1
    print("OK packet complete, every %s finding has evidence" % args.fail_on)
    return 0


if __name__ == "__main__":
    sys.exit(main())
