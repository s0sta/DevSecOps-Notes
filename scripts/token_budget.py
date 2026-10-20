#!/usr/bin/env python3
"""token_budget.py - estimate LLM tokens and project a monthly bill.

Estimates tokens from character counts (about four characters per token by
default), prices input and output separately from a JSON config, and projects
a monthly bill from a JSONL file of request counts.

Config JSON, one object:
    {"model": "example-large", "chars_per_token": 4,
     "price_in": 3.0, "price_out": 15.0}

Request JSONL, one workload per line:
    {"name": "chat", "requests": 120000,
     "input_chars": 1600, "output_chars": 600}

Read-only: it reads files and never writes one. Exit codes: 0 within budget
(or no budget given), 1 over budget, 2 usage or input error.

Usage:
    python3 token_budget.py budget.json requests.jsonl --budget 500
    python3 token_budget.py budget.json requests.jsonl
    cat requests.jsonl | python3 token_budget.py budget.json -
    python3 token_budget.py budget.json requests.jsonl --budget 500 --json
    python3 token_budget.py budget.json requests.jsonl --chars-per-token 3.5

Cron (monthly, first day at 07:00):
    0 7 1 * * python3 token_budget.py budget.json requests.jsonl --budget 500

CI gate (fails the build when the month is over budget):
    python3 token_budget.py budget.json requests.jsonl --budget 500

By s0sta.com
"""
import argparse
import json
import sys

DEFAULT_CHARS_PER_TOKEN = 4.0


def is_number(value):
    """True for an int or float that is not a bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def load_config(path, errors):
    """Read and validate the price config. Returns a dict or None."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            config = json.load(handle)
    except OSError as exc:
        errors.append("%s: %s" % (path, exc))
        return None
    except ValueError as exc:
        errors.append("%s: not JSON: %s" % (path, exc))
        return None
    if not isinstance(config, dict):
        errors.append("%s: expected a JSON object" % path)
        return None
    for key in ("price_in", "price_out"):
        value = config.get(key)
        if not is_number(value) or value < 0:
            errors.append("%s: %s must be a number >= 0" % (path, key))
            return None
    cpt = config.get("chars_per_token", DEFAULT_CHARS_PER_TOKEN)
    if not is_number(cpt) or cpt <= 0:
        errors.append("%s: chars_per_token must be a number > 0" % path)
        return None
    return config


def load_rows(path, errors):
    """Read one JSONL file of workloads. Returns a list of dicts."""
    label = "<stdin>" if path == "-" else path
    try:
        if path == "-":
            text = sys.stdin.read()
        else:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
    except OSError as exc:
        errors.append("%s: %s" % (label, exc))
        return []

    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            errors.append("%s:%d: not JSON: %s" % (label, lineno, exc))
            continue
        if not isinstance(row, dict):
            errors.append("%s:%d: expected a JSON object" % (label, lineno))
            continue
        name = str(row.get("name", "workload-%d" % lineno))
        requests = row.get("requests", 1)
        input_chars = row.get("input_chars")
        output_chars = row.get("output_chars")
        if not is_number(requests) or requests < 0:
            errors.append("%s:%d: requests must be a number >= 0" % (label, lineno))
            continue
        if not is_number(input_chars) or input_chars < 0:
            errors.append("%s:%d: input_chars missing or < 0" % (label, lineno))
            continue
        if not is_number(output_chars) or output_chars < 0:
            errors.append("%s:%d: output_chars missing or < 0" % (label, lineno))
            continue
        rows.append({"name": name, "requests": requests,
                     "input_chars": float(input_chars),
                     "output_chars": float(output_chars)})
    return rows


def price_rows(rows, config, cpt):
    """Add token counts and a monthly USD cost to each workload."""
    price_in = float(config["price_in"])
    price_out = float(config["price_out"])
    priced = []
    for row in rows:
        in_tokens = row["input_chars"] / cpt
        out_tokens = row["output_chars"] / cpt
        cost = row["requests"] * (in_tokens * price_in
                                  + out_tokens * price_out) / 1e6
        item = dict(row)
        item["in_tokens"] = in_tokens
        item["out_tokens"] = out_tokens
        item["cost"] = cost
        priced.append(item)
    return priced


def print_table(priced):
    print("%-24s %10s %11s %12s %13s"
          % ("WORKLOAD", "REQUESTS", "INPUT TOK", "OUTPUT TOK", "USD/MONTH"))
    for item in priced:
        print("%-24s %10d %11.0f %12.0f %13.2f"
              % (item["name"][:24], item["requests"], item["in_tokens"],
                 item["out_tokens"], item["cost"]))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Estimate tokens from characters and project a monthly "
                    "LLM bill. Exits 1 when the month is over budget.")
    parser.add_argument("config", help="JSON file with price_in and price_out")
    parser.add_argument("requests", nargs="+", metavar="REQUESTS",
                        help="JSONL file(s) of workloads, or - for stdin")
    parser.add_argument("-b", "--budget", type=float,
                        help="monthly budget in USD; exit 1 when over it")
    parser.add_argument("-c", "--chars-per-token", type=float,
                        help="override chars_per_token from the config")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only, no table")
    parser.add_argument("--json", action="store_true",
                        help="print one machine-readable JSON object")
    args = parser.parse_args(argv)

    if args.budget is not None and args.budget < 0:
        parser.error("--budget must be >= 0")
    if args.chars_per_token is not None and args.chars_per_token <= 0:
        parser.error("--chars-per-token must be > 0")

    errors = []
    config = load_config(args.config, errors)
    rows = []
    for path in args.requests:
        rows.extend(load_rows(path, errors))

    for message in errors:
        print("error: %s" % message, file=sys.stderr)
    if errors:
        return 2
    if not rows:
        print("error: no workload rows found", file=sys.stderr)
        return 2

    cpt = (args.chars_per_token if args.chars_per_token is not None
           else float(config.get("chars_per_token", DEFAULT_CHARS_PER_TOKEN)))
    priced = price_rows(rows, config, cpt)
    total = sum(item["cost"] for item in priced)
    budget = args.budget

    if args.json:
        print(json.dumps({
            "model": config.get("model"),
            "chars_per_token": cpt,
            "monthly_usd": round(total, 2),
            "budget_usd": budget,
            "over": budget is not None and total > budget,
            "workloads": [{"name": item["name"],
                           "requests": item["requests"],
                           "input_tokens": round(item["in_tokens"]),
                           "output_tokens": round(item["out_tokens"]),
                           "usd_month": round(item["cost"], 2)}
                          for item in priced],
        }, sort_keys=True))
        return 1 if budget is not None and total > budget else 0

    if not args.quiet:
        print_table(priced)
        print()

    if budget is None:
        print("MONTHLY $%.2f" % total)
        return 0
    print("MONTHLY $%.2f BUDGET $%.2f" % (total, budget))
    if total > budget:
        print("ALERT over by $%.2f" % (total - budget))
        return 1
    print("OK under by $%.2f" % (budget - total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
