---
id: p264
title: "An LLM gateway log audit in Python"
slug: an-llm-gateway-log-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [LLM, Python, DevSecOps, AIEngineering, CloudNative]
source: "LinkedIn post P264 · Platform series"
linkedin_date: 2028-06-04
design: code
script: llm_audit.py
---

# An LLM gateway log audit in Python

Every prompt through your gateway becomes a log line, and most teams keep those lines for debugging and never read them. That log is a security control: it shows what users asked, what the model answered, and what your filters missed.

## Quick reference

The full script is at the end of this note: **llm_audit.py** (standard library only, no `pip install`).

**Run it**

```bash
python3 llm_audit.py gateway.jsonl
```

**Example output**

```text
ALERT PII 2 INJECTION 1 TOKENS 203
```

## Explained

### What it does

The script reads a JSONL export where each line is one request and response. It runs PII regexes over both fields, looks for injection markers such as "ignore previous instructions", totals the token counts, and computes the refusal rate from the response text.

### Why audit it

A prompt that reaches the model with an email address in it has already left your boundary, whether or not the answer repeats it. Injection markers show attempts that your input filter did not stop. The refusal rate is a cheap drift signal: if it jumps, a prompt change or a model change broke something.

### How to use it

Point it at an export from the gateway: `python3 llm_audit.py gateway.jsonl`. It prints one summary and a few sample hits, and exits 1 when it finds a policy problem, so a nightly job can alert on it.

> **The honest caveat:** a regex catches patterns, not intent, so treat a hit as a lead to review, not a verdict. A prompt log is also a second copy of the leak, so redact before you archive it.

> **The lesson:** if you log prompts, audit them like production data, because that is what they are.

## In one line

> **A log is a control.** You cannot review what you never recorded.

**Run it weekly**

```bash
python3 llm_audit.py gateway.jsonl
```

## Script: llm_audit.py

Download: [scripts/llm_audit.py](../scripts/llm_audit.py)

```python
#!/usr/bin/env python3
"""llm_audit.py - audit an LLM gateway log for PII, injection and refusals.

Reads a JSONL export from an LLM gateway: one JSON object per line, with the
prompt and the response. Reports the four things a policy review needs:

    PII patterns        email, phone and card numbers in either field
    injection markers   "ignore previous instructions", "system prompt", ...
    tokens              total from usage, or prompt plus completion counts
    refusal rate        responses that read as a refusal

Prompts are read from "prompt"/"input" or a "messages" list; responses from
"response"/"completion"/"output". Nothing is written and no provider is
called. Exit codes: 0 clean, 1 a policy finding, 2 usage or read error.

Usage:
    python3 llm_audit.py gateway.jsonl
    cat gateway.jsonl | python3 llm_audit.py -
    python3 llm_audit.py logs/*.jsonl --max-refusal 0.15
    python3 llm_audit.py gateway.jsonl --json --quiet

CI:
    python3 llm_audit.py logs/export.jsonl --max-refusal 0.2 || exit 1
Cron (nightly at 01:30):
    30 1 * * * cd /srv/gateway && python3 llm_audit.py logs/export.jsonl >> /var/log/llm_audit.log 2>&1

By s0sta.com
"""
import argparse
import json
import re
import sys
from contextlib import nullcontext

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+\d[\d ()-]{7,}\d")
CARD = re.compile(r"\b(?:\d[ -]?){15}\d\b")

INJECTION = (
    "ignore previous", "ignore all previous", "ignore the above",
    "disregard previous", "disregard the above", "forget your instructions",
    "system prompt", "you are now", "new instructions", "reveal your",
    "print your instructions", "jailbreak",
)

REFUSAL = (
    "i can't assist", "i cannot assist", "i can't help with",
    "i cannot help with", "i'm sorry, but i can't", "i must decline",
    "i can't provide", "i cannot provide", "i am unable to",
    "i'm not able to",
)


def luhn(number):
    """True when the digits pass the Luhn checksum."""
    digits = [int(c) for c in number if c.isdigit()]
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def mask(kind, value):
    """Return a value that is safe to print in a report."""
    if kind == "email":
        user, _, domain = value.partition("@")
        return (user[:1] + "***@" + domain) if user else "***@" + domain
    digits = "".join(c for c in value if c.isdigit())
    return "***" + digits[-4:] if len(digits) >= 4 else "***"


def pii_hits(text):
    """Yield (kind, masked value) for every PII match in text."""
    for match in EMAIL.finditer(text):
        yield "email", mask("email", match.group(0))
    for match in PHONE.finditer(text):
        yield "phone", mask("phone", match.group(0))
    for match in CARD.finditer(text):
        value = match.group(0)
        if luhn(value):
            yield "card", mask("card", value)


def injection_hits(text):
    """Return the injection markers present in text, in list order."""
    low = text.lower()
    return [marker for marker in INJECTION if marker in low]


def refused(response):
    """True when the response reads as a refusal."""
    low = response.lower()
    return any(phrase in low for phrase in REFUSAL)


def prompt_of(record):
    for key in ("prompt", "input"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    messages = record.get("messages")
    if isinstance(messages, list):
        parts = [str(m.get("content", "")) for m in messages if isinstance(m, dict)]
        return " ".join(part for part in parts if part)
    return ""


def response_of(record):
    for key in ("response", "completion", "output"):
        value = record.get(key)
        if isinstance(value, str):
            return value
    return ""


def tokens_of(record):
    """Total tokens from usage, preferring total_tokens."""
    usage = record.get("usage")
    if not isinstance(usage, dict):
        return 0
    total = usage.get("total_tokens")
    if isinstance(total, int):
        return total
    return sum(v for k, v in usage.items()
               if k.endswith("_tokens") and isinstance(v, int))


def iter_records(paths, open_errors, bad_lines):
    """Yield one dict per JSONL record; collect unreadable input."""
    for path in paths:
        label = "<stdin>" if path == "-" else path
        try:
            cm = nullcontext(sys.stdin) if path == "-" else open(
                path, "r", encoding="utf-8", errors="replace")
        except OSError as exc:
            open_errors.append("%s: %s" % (label, exc))
            continue
        with cm as handle:
            for line_no, line in enumerate(handle, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except ValueError:
                    bad_lines.append("%s:%d not JSON" % (label, line_no))
                    continue
                if not isinstance(record, dict):
                    bad_lines.append("%s:%d not an object" % (label, line_no))
                    continue
                yield record


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Audit an LLM gateway JSONL log for PII, injection, "
                    "token totals and refusals.")
    ap.add_argument("paths", nargs="*", default=["-"], metavar="PATH",
                    help="JSONL export, or - for stdin (default)")
    ap.add_argument("--max-refusal", type=float, metavar="RATE",
                    help="fail when the refusal rate is above this, e.g. 0.2")
    ap.add_argument("--show", type=int, default=3, metavar="N",
                    help="sample hits to print per category, default 3")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="print the summary only")
    ap.add_argument("--json", action="store_true",
                    help="print one machine-readable JSON object")
    args = ap.parse_args(argv)

    if args.max_refusal is not None and not 0.0 <= args.max_refusal <= 1.0:
        ap.error("--max-refusal must be between 0 and 1")
    if args.show < 0:
        ap.error("--show must be 0 or more")

    open_errors, bad_lines = [], []
    records = responses = tokens = refusals = 0
    pii = {"email": 0, "phone": 0, "card": 0}
    samples = {"email": [], "phone": [], "card": []}
    injection_records = 0
    injection_samples = []

    for record in iter_records(args.paths, open_errors, bad_lines):
        prompt = prompt_of(record)
        response = response_of(record)
        text = prompt + "\n" + response
        records += 1
        if response:
            responses += 1
            if refused(response):
                refusals += 1
        tokens += tokens_of(record)
        for kind, masked in pii_hits(text):
            pii[kind] += 1
            if len(samples[kind]) < args.show:
                samples[kind].append(masked)
        markers = injection_hits(text)
        if markers:
            injection_records += 1
            if len(injection_samples) < args.show:
                injection_samples.append((records, markers))

    for message in open_errors:
        print("error: %s" % message, file=sys.stderr)
    if open_errors:
        return 2
    if not records:
        print("no JSONL records in %s" % " ".join(args.paths), file=sys.stderr)
        return 2
    for message in bad_lines[:5]:
        print("warn: skipped %s" % message, file=sys.stderr)

    rate = (refusals / responses) if responses else 0.0
    pii_total = sum(pii.values())
    findings = pii_total + injection_records
    over_limit = args.max_refusal is not None and rate > args.max_refusal
    if over_limit:
        findings += 1

    if args.json:
        print(json.dumps({
            "records": records,
            "responses": responses,
            "skipped": len(bad_lines),
            "tokens": tokens,
            "refusals": refusals,
            "refusal_rate": round(rate, 4),
            "pii": pii,
            "pii_total": pii_total,
            "injection_records": injection_records,
            "findings": findings,
        }, sort_keys=True))
        return 1 if findings else 0

    print("%d record(s), %d response(s), %d skipped"
          % (records, responses, len(bad_lines)))
    print("tokens %d" % tokens)
    print("refusals %d  rate %.1f%%" % (refusals, rate * 100))
    print("PII %d  email %d  phone %d  card %d"
          % (pii_total, pii["email"], pii["phone"], pii["card"]))
    print("INJECTION %d record(s)" % injection_records)

    if not args.quiet:
        for kind in ("email", "phone", "card"):
            for value in samples[kind]:
                print("  PII %-5s %s" % (kind, value))
        for number, markers in injection_samples:
            print("  INJECTION record %d: %s" % (number, ", ".join(markers)))

    if over_limit:
        print("REFUSAL %.1f%% above the %.1f%% limit"
              % (rate * 100, args.max_refusal * 100))
    print("ALERT %d finding(s)" % findings if findings else "OK clean")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
```
