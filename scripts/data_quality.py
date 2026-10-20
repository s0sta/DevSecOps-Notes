#!/usr/bin/env python3
"""Check JSONL rows against a small rules file and report the violations.

Usage:
    python3 data_quality.py rows.jsonl rules.json
    python3 data_quality.py rows.jsonl rules.json --json
    python3 data_quality.py rows.jsonl rules.json --limit 5
    python3 data_quality.py --help

rows.jsonl is one JSON object per line.  The rules file is JSON:

    {"required": ["id", "email"],
     "unique":   ["id"],
     "ranges":   {"amount": [0, 10000]}}

Every row is checked for missing required fields, duplicate unique keys and
out-of-range numbers.  Findings print one per row, then the count of findings
against the number of rows read.  A malformed line is a finding, not a crash.

Exit codes: 0 no findings, 1 findings, 2 usage or input error.
Read-only: the script never writes to the rows or to the rules file.

CI:   python3 data_quality.py rows.jsonl rules.json || exit 1
Cron: 15 3 * * * python3 data_quality.py rows.jsonl rules.json >> /var/log/dq.log 2>&1

By s0sta.com
"""
import argparse
import json
import sys

EMPTY = (None, "")


def load_rules(path):
    """Read and validate the rules file. Raises ValueError on a bad rule."""
    with open(path, "r") as fh:
        rules = json.load(fh)
    if not isinstance(rules, dict):
        raise ValueError("rules must be a JSON object")

    for key in ("required", "unique"):
        value = rules.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError("%s must be a list of field names" % key)

    ranges = rules.get("ranges", {})
    if not isinstance(ranges, dict):
        raise ValueError("ranges must be an object of field: [min, max]")
    clean = {}
    for field, spec in ranges.items():
        if (not isinstance(spec, list) or len(spec) != 2
                or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in spec)):
            raise ValueError("range for %r must be [min, max] numbers" % field)
        low, high = spec
        if low > high:
            raise ValueError("range for %r has min above max" % field)
        clean[field] = (low, high)

    return {
        "required": rules.get("required", []),
        "unique": rules.get("unique", []),
        "ranges": clean,
    }


def kind_of(message):
    """Map a message to a rule name for the JSON summary."""
    if message.startswith("missing "):
        return "required"
    if message.startswith("duplicate ") or message.startswith("unhashable "):
        return "unique"
    return "range"


def check_row(row, rules, seen):
    """Return the list of problems for one row, and remember unique values."""
    problems = []

    for field in rules["required"]:
        if row.get(field) in EMPTY:
            problems.append("missing " + field)

    for field in rules["unique"]:
        value = row.get(field)
        if value is None:
            continue
        try:
            hash(value)
        except TypeError:
            problems.append("unhashable " + field)
            continue
        if value in seen[field]:
            problems.append("duplicate %s=%r" % (field, value))
        else:
            seen[field].add(value)

    for field, (low, high) in rules["ranges"].items():
        value = row.get(field)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            problems.append("%s is not numeric" % field)
        elif not low <= value <= high:
            problems.append("%s %s out of range %s..%s" % (field, value, low, high))

    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check JSONL rows for missing fields, duplicates and out-of-range numbers.",
        epilog="Exit 0 clean, 1 findings, 2 usage or input error. Read-only.",
    )
    parser.add_argument("rows", help="path to the JSONL rows file")
    parser.add_argument("rules", help="path to the rules JSON file")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON object instead of lines")
    parser.add_argument("--limit", type=int, default=50,
                        help="maximum findings to print, 0 for all (default 50)")
    args = parser.parse_args(argv)
    if args.limit < 0:
        print("error: --limit cannot be negative", file=sys.stderr)
        return 2

    try:
        rules = load_rules(args.rules)
    except json.JSONDecodeError as exc:
        print("error: %s is not valid JSON: %s" % (args.rules, exc), file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    seen = {field: set() for field in rules["unique"]}
    findings = []
    rows = 0

    try:
        fh = open(args.rows, "r")
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    with fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            rows += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                findings.append({"row": rows, "line": line_no, "rule": "parse",
                                 "message": "invalid json: %s" % exc.msg})
                continue
            if not isinstance(row, dict):
                findings.append({"row": rows, "line": line_no, "rule": "parse",
                                 "message": "not a JSON object"})
                continue
            for message in check_row(row, rules, seen):
                findings.append({"row": rows, "line": line_no,
                                 "rule": kind_of(message), "message": message})

    if args.json:
        by_rule = {}
        for f in findings:
            by_rule[f["rule"]] = by_rule.get(f["rule"], 0) + 1
        print(json.dumps({
            "rows": rows,
            "findings": len(findings),
            "by_rule": by_rule,
            "violations": findings,
        }, indent=2, sort_keys=True))
    else:
        shown = findings if args.limit == 0 else findings[:args.limit]
        for f in shown:
            print("row %d: %s" % (f["row"], f["message"]))
        if len(findings) > len(shown):
            print("... %d more findings" % (len(findings) - len(shown)))
        print("findings: %d in %d rows" % (len(findings), rows))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
