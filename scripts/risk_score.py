#!/usr/bin/env python3
"""Score a JSON risk register and fail when a risk is over the appetite.

Usage:
    python3 risk_score.py register.json
    python3 risk_score.py register.json --appetite 12
    python3 risk_score.py --help

The register is a JSON object with a "risks" list. A bare list also works.
Each risk needs: id, asset, likelihood (1-5), impact (1-5), owner, status.
The score is likelihood x impact, so it runs from 1 to 25. The script ranks
every risk, prints the table, and exits 1 when any score is above --appetite.

Exit codes:
    0  every score is at or below the appetite
    1  at least one score is above the appetite
    2  usage error, unreadable file, invalid JSON or invalid field

The register is opened read-only and is never modified.

Cron/CI:
    0 7 * * 1 python3 risk_score.py /etc/risk/register.json --appetite 15
    python3 risk_score.py register.json --appetite 15 || exit 1

By s0sta.com
"""
import argparse
import json
import sys
from pathlib import Path

FIELDS = ("id", "asset", "likelihood", "impact", "owner", "status")


class RegisterError(Exception):
    """The register or one of its fields is not usable."""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Score a JSON risk register (likelihood x impact) and gate on an appetite.",
    )
    parser.add_argument("register", help="path to the JSON register")
    parser.add_argument(
        "--appetite",
        type=int,
        default=15,
        metavar="N",
        help="highest score allowed without failing, 1-25 (default: 15)",
    )
    return parser.parse_args(argv)


def load_register(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RegisterError("cannot read %s: %s" % (path, exc))
    try:
        document = json.loads(raw)
    except ValueError as exc:
        raise RegisterError("invalid JSON in %s: %s" % (path, exc))
    if isinstance(document, dict):
        document = document.get("risks")
    if not isinstance(document, list):
        raise RegisterError('register must be a list or an object with a "risks" list')
    return document


def validate(rows):
    scored = []
    seen = set()
    for index, row in enumerate(rows, 1):
        where = "risk %d" % index
        if not isinstance(row, dict):
            raise RegisterError("%s: expected an object" % where)
        missing = [field for field in FIELDS if field not in row]
        if missing:
            raise RegisterError("%s: missing %s" % (where, ", ".join(missing)))
        risk_id = row["id"]
        if not isinstance(risk_id, str) or not risk_id.strip():
            raise RegisterError("%s: id must be a non-empty string" % where)
        if risk_id in seen:
            raise RegisterError("%s: duplicate id %s" % (where, risk_id))
        seen.add(risk_id)
        for field in ("likelihood", "impact"):
            value = row[field]
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
                raise RegisterError("%s: %s must be an integer 1-5" % (where, field))
        for field in ("asset", "owner", "status"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise RegisterError("%s: %s must be a non-empty string" % (where, field))
        scored.append(
            {
                "score": row["likelihood"] * row["impact"],
                "id": risk_id,
                "asset": row["asset"],
                "owner": row["owner"],
                "status": row["status"],
            }
        )
    scored.sort(key=lambda item: (-item["score"], item["id"]))
    return scored


def print_table(scored):
    asset_width = max(len(item["asset"]) for item in scored)
    owner_width = max(8, max(len(item["owner"]) for item in scored))
    print("%5s  %-8s  %-*s  %-*s  %s" % (
        "SCORE", "ID", asset_width, "ASSET", owner_width, "OWNER", "STATUS"))
    for item in scored:
        print("%5d  %-8s  %-*s  %-*s  %s" % (
            item["score"], item["id"], asset_width, item["asset"],
            owner_width, item["owner"], item["status"]))


def main(argv=None):
    args = parse_args(argv)
    if not 1 <= args.appetite <= 25:
        print("risk_score.py: error: --appetite must be 1-25", file=sys.stderr)
        return 2
    try:
        scored = validate(load_register(args.register))
    except RegisterError as exc:
        print("risk_score.py: error: %s" % exc, file=sys.stderr)
        return 2

    if not scored:
        print("OK no risks in register")
        return 0

    print_table(scored)
    over = [item for item in scored if item["score"] > args.appetite]
    if over:
        print("ALERT %d over appetite %d" % (len(over), args.appetite))
        print("top %d %s %s" % (over[0]["score"], over[0]["id"], over[0]["asset"]))
        return 1
    print("OK %d risk%s, all at or below appetite %d" % (
        len(scored), "" if len(scored) == 1 else "s", args.appetite))
    return 0


if __name__ == "__main__":
    sys.exit(main())
