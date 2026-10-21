#!/usr/bin/env python3
"""Compare two scan exports and show what the fix actually changed.

Reads a before export and an after export:

    {"tool": "scanner",
     "checks": ["CIS-1.1.0", "CIS-2.1.0", "CIS-3.4.1"],
     "findings": [
         {"asset": "api-01", "check": "CIS-1.1.0",
          "title": "SSH root login", "severity": "high"},
         ...]}

A finding is identified by (asset, check), not by the scanner's finding id:
ids change between runs, while an asset and the check that failed do not. The
diff then reports:

  * closed  in before, not in after
  * still   in both
  * new     in after, not in before
  * hidden  closed, but the check no longer appears in after.checks

The hidden list is the point of the script. A finding can disappear because
somebody fixed it, or because somebody stopped running the check. Both look
like a closed finding in a dashboard; only the check list tells them apart. An
after export without a checks list is rejected, because a closure cannot be
proven when nobody recorded which checks ran.

Usage:
    python3 rescan_diff.py before.json after.json
    python3 rescan_diff.py before.json after.json --allow-new

Exit codes: 0 no new finding and no hidden fix, 1 a new finding or a hidden
fix, 2 usage or invalid input.

CI (run after the patch window, fail the job on a regression):
    python3 rescan_diff.py before.json after.json

Cron (daily, after the overnight scan lands):
    30 5 * * * python3 /opt/s0sta/rescan_diff.py /exports/yesterday.json /exports/today.json

The script is read-only: two JSON files, no scanner, no API calls, no writes.
--allow-new exists for a scan that legitimately widens its scope; it does not
suppress hidden fixes. The diff can only see what both exports cover: if an
asset left the after export entirely, its findings count as closed, and no
check list can tell you that the asset was dropped.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys


class DiffError(Exception):
    """Anything that should end the run with exit code 2."""


def load_json(source, label):
    """Read JSON from a path, or stdin when source is '-'."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise DiffError("cannot read %s: %s" % (label, exc))
    except ValueError as exc:
        raise DiffError("%s is not valid JSON: %s" % (label, exc))


def read_export(doc, label, need_checks):
    """Return (findings set, checks set) for one export."""
    if not isinstance(doc, dict):
        raise DiffError("%s must be a JSON object" % label)
    findings = doc.get("findings")
    checks = doc.get("checks")
    if not isinstance(findings, list):
        raise DiffError("%s needs a findings list" % label)
    if need_checks and not isinstance(checks, list):
        raise DiffError("%s needs a checks list to prove which checks ran"
                        % label)
    if checks is None:
        checks = []
    if not isinstance(checks, list) or not all(isinstance(c, str) for c in checks):
        raise DiffError("%s checks must be a list of strings" % label)
    pairs = set()
    for number, item in enumerate(findings, 1):
        if not isinstance(item, dict):
            raise DiffError("%s finding %d is not an object" % (label, number))
        asset = item.get("asset")
        check = item.get("check")
        if not isinstance(asset, str) or not asset.strip():
            raise DiffError("%s finding %d needs an asset" % (label, number))
        if not isinstance(check, str) or not check.strip():
            raise DiffError("%s finding %d needs a check" % (label, number))
        pairs.add((asset.strip(), check.strip()))
    return pairs, {check.strip() for check in checks if check.strip()}


def count(number, one, many):
    """Return '1 finding' or '2 findings'."""
    return "%d %s" % (number, one if number == 1 else many)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Diff two scan exports: closed, still open, new, and "
                    "closures caused by a check that stopped running.",
        epilog="Exit codes: 0 clean, 1 new finding or hidden fix, 2 usage or "
               "input error.")
    parser.add_argument("before", help="scan export from before the fix")
    parser.add_argument("after", help="scan export from after the fix")
    parser.add_argument("--allow-new", action="store_true",
                        help="do not fail on new findings (hidden fixes still fail)")
    args = parser.parse_args(argv)

    try:
        before, before_checks = read_export(
            load_json(args.before, "before export"), "before", False)
        after, after_checks = read_export(
            load_json(args.after, "after export"), "after", True)
    except DiffError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    closed = sorted(before - after)
    still = sorted(before & after)
    new = sorted(after - before)
    hidden = [pair for pair in closed if pair[1] not in after_checks]

    per_asset = {}
    for asset, _check in before:
        per_asset[asset] = per_asset.get(asset, 0) - 1
    for asset, _check in after:
        per_asset[asset] = per_asset.get(asset, 0) + 1
    moved = sorted((asset, delta) for asset, delta in per_asset.items() if delta)

    print("BEFORE %d findings, %d checks, AFTER %d findings, %d checks"
          % (len(before), len(before_checks), len(after), len(after_checks)))

    def pair_list(pairs):
        return ", ".join("%s %s" % pair for pair in pairs)

    if closed:
        print("CLOSED %d: %s" % (len(closed), pair_list(closed)))
    if still:
        print("STILL %d: %s" % (len(still), pair_list(still)))
    if new:
        print("NEW %d: %s" % (len(new), pair_list(new)))
    if moved:
        print("PER ASSET %s" % ", ".join(
            "%s %+d" % (asset, delta) for asset, delta in moved))
    if hidden:
        print("HIDDEN %d: %s" % (len(hidden), ", ".join(
            "%s %s (no check after)" % pair for pair in hidden)))

    failed = bool(hidden) or (bool(new) and not args.allow_new)
    if failed:
        parts = []
        if new and not args.allow_new:
            parts.append(count(len(new), "new finding", "new findings"))
        if hidden:
            parts.append(count(len(hidden), "hidden fix", "hidden fixes"))
        print("FAIL %s" % ", ".join(parts))
        return 1
    if new:
        print("OK %d closed, %d still open, %d new allowed"
              % (len(closed), len(still), len(new)))
    else:
        print("OK %d closed, %d still open, nothing new"
              % (len(closed), len(still)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
