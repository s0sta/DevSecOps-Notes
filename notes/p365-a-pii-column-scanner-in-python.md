---
id: p365
title: "A PII column scanner in Python"
slug: a-pii-column-scanner-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [DataGovernance, PII, Python, Privacy, DataEngineering]
source: "LinkedIn post P365 · Data series"
linkedin_date: 2029-01-25
design: code
script: pii_columns.py
---

# A PII column scanner in Python

The security review asks one question you cannot answer from memory: which columns hold personal data? The schema knows, if you read it properly.

## Quick reference

The full script is at the end of this note: **pii_columns.py** (standard library only, no `pip install`).

**Run it**

```bash
python3 pii_columns.py schema.json
```

**Example output**

```text
PII: users.email, users.dob, events.ip
columns: 3 tables: 2
```

## Explained

### What it runs

The schema is JSON: a tables key, and each table a list of columns with a name and a type. It splits every column name into tokens and compares them to a list such as email, phone, ssn, dob, address, name, passport, iban, card and ip. A match is a hit.

### What the types add

Some columns are personal whatever the name. inet is an IP address, json and jsonb can hold a free-text form, and bytea can hold a scanned document. Flagged for review, not as proof.

### What it prints

One line of flagged columns, then a summary line. Exit 1 when anything is flagged, 0 when clean, and 2 when the file is missing or not JSON, because a check that cannot run is not a pass.

### How to use it

Run it in CI against the schema dump, or weekly from cron and diff it: a new column is the event you want to see. The full script adds `--json` and one line per column.

> **The honest caveat:** a name list is a guess. A column called notes can hold an email address and pass, a name in another language is invisible, and a bare name column is flagged whether it holds a person or a product.

> **The lesson:** start with the schema, then sample the values. Neither one alone is discovery.

## In one line

> **The schema is the short list.** A name pattern is a hypothesis; the schema is where you start.

**Run it on a dump**

```bash
python3 pii_columns.py schema.json
```

## Script: pii_columns.py

Download: [scripts/pii_columns.py](../scripts/pii_columns.py)

```python
#!/usr/bin/env python3
"""Scan a JSON schema for columns that probably hold personal data.

Usage:
    python3 pii_columns.py schema.json
    python3 pii_columns.py schema.json --json
    python3 pii_columns.py schema.json --quiet
    python3 pii_columns.py --help

The schema file is JSON, either wrapped in a "tables" key or bare:

    {"tables": {"users": [{"name": "email", "type": "text"},
                          {"name": "date_of_birth", "type": "date"}]}}

A column may also be written as the string "email text".  Column names are
split on punctuation and camel case, then matched against a short list of
personal-data tokens.  Types that can hide data whatever the name (inet, json,
jsonb, bytea) are reported for review, not as proof.

Exit codes: 0 no findings, 1 findings, 2 usage or input error.
Read-only: the script never writes to the schema or to a database.

CI:   python3 pii_columns.py schema.json || exit 1
Cron: 0 6 * * 1 python3 pii_columns.py schema.json >> /var/log/pii.log 2>&1

By s0sta.com
"""
import argparse
import json
import re
import sys

# token -> category. Keep it short and boring; every entry is a guess.
NAME_HINTS = {
    "email": "email",
    "mail": "email",
    "phone": "phone",
    "mobile": "phone",
    "tel": "phone",
    "telephone": "phone",
    "ssn": "national id",
    "nino": "national id",
    "passport": "national id",
    "licence": "national id",
    "license": "national id",
    "tax": "national id",
    "dob": "date of birth",
    "birth": "date of birth",
    "birthdate": "date of birth",
    "address": "address",
    "street": "address",
    "postcode": "address",
    "zip": "address",
    "postal": "address",
    "name": "name",
    "surname": "name",
    "forename": "name",
    "given": "name",
    "family": "name",
    "card": "payment card",
    "pan": "payment card",
    "cvv": "payment card",
    "iban": "bank account",
    "bic": "bank account",
    "ip": "ip address",
    "ipv4": "ip address",
    "ipv6": "ip address",
    "latitude": "location",
    "longitude": "location",
    "geo": "location",
    "location": "location",
    "health": "special category",
    "diagnosis": "special category",
    "religion": "special category",
    "ethnicity": "special category",
    "biometric": "special category",
    "salary": "financial",
}

# type -> category. These hold personal data whatever the column is called.
TYPE_HINTS = {
    "inet": "ip address",
    "json": "free-form json",
    "jsonb": "free-form json",
    "bytea": "binary blob",
}

# Metadata columns that contain a hint token but are not personal data.
IGNORE = {
    "table_name",
    "column_name",
    "schema_name",
    "index_name",
    "file_name",
    "constraint_name",
    "product_name",
    "company_name",
    "model_name",
}


def tokens(name):
    """Split a column name into lowercase tokens: dateOfBirth -> date, of, birth."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name))
    return [t for t in re.split(r"[^a-z0-9]+", spaced.lower()) if t]


def base_type(typ):
    """text[] and varchar(255) both reduce to their base type."""
    return str(typ).split("(")[0].strip().lower().rstrip("[]").strip()


def load_schema(path):
    """Read the schema file and return the table mapping."""
    with open(path, "r") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("schema must be a JSON object")
    tables = data.get("tables", data.get("schema", data))
    if not isinstance(tables, dict):
        raise ValueError("tables must be a JSON object of table: columns")
    return tables


def iter_columns(tables):
    """Yield (table, column, type) for every column in the schema."""
    for table, cols in tables.items():
        if isinstance(cols, dict) and "columns" in cols:
            cols = cols["columns"]
        if isinstance(cols, dict):
            cols = [{"name": k, "type": v} for k, v in cols.items()]
        if not isinstance(cols, list):
            raise ValueError("table %r must be a list of columns" % table)
        for col in cols:
            if isinstance(col, str):
                parts = col.split(None, 1)
                if not parts:
                    raise ValueError("empty column in table %r" % table)
                yield table, parts[0], parts[1] if len(parts) > 1 else "unknown"
            elif isinstance(col, dict):
                name = col.get("name") or col.get("column")
                if not name:
                    raise ValueError("column without a name in table %r" % table)
                yield table, str(name), str(col.get("type", "unknown"))
            else:
                raise ValueError("column in table %r must be an object or string" % table)


def scan(tables):
    """Return the findings, sorted by table and column."""
    findings = []
    for table, column, typ in iter_columns(tables):
        lower = str(column).lower()
        hit = None
        if lower not in IGNORE:
            for token in tokens(column):
                if token in NAME_HINTS:
                    hit = ("name", NAME_HINTS[token])
                    break
        if hit is None:
            base = base_type(typ)
            if base in TYPE_HINTS:
                hit = ("type", TYPE_HINTS[base])
        if hit:
            findings.append({
                "table": table,
                "column": column,
                "type": typ,
                "kind": hit[0],
                "category": hit[1],
            })
    findings.sort(key=lambda f: (str(f["table"]), str(f["column"])))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Flag columns that probably hold personal data, from a schema JSON.",
        epilog="Exit 0 clean, 1 findings, 2 usage or input error. Read-only.",
    )
    parser.add_argument("schema", help="path to the schema JSON file")
    parser.add_argument("--json", action="store_true",
                        help="print one JSON object instead of lines")
    parser.add_argument("--quiet", action="store_true",
                        help="print only the summary line")
    args = parser.parse_args(argv)

    try:
        tables = load_schema(args.schema)
    except json.JSONDecodeError as exc:
        print("error: %s is not valid JSON: %s" % (args.schema, exc), file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    try:
        findings = scan(tables)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "schema": args.schema,
            "tables": len(tables),
            "count": len(findings),
            "findings": findings,
        }, indent=2, sort_keys=True))
    else:
        if not args.quiet:
            for f in findings:
                label = ("name:" if f["kind"] == "name" else "type:") + f["category"]
                print("%-34s %-12s %s" % (f["table"] + "." + f["column"], f["type"], label))
        print("PII columns: %d in %d tables" % (len(findings), len(tables)))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
```
