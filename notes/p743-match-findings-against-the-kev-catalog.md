---
id: p743
title: "Match findings against the KEV catalog"
slug: match-findings-against-the-kev-catalog
sections: [devsecops]
topic: "Python scripts"
tags: [CISAKEV, VulnerabilityManagement, ThreatIntel, PatchManagement, CyberSecurity]
source: "LinkedIn post P743 · ASM series"
linkedin_date: 2031-06-26
design: code
script: kev_match.py
---

# Match findings against the KEV catalog

The finding sat in the medium pile for five months. CVSS said 6.5; KEV said exploited in the wild since March, with a due date already passed.

## Quick reference

The full script is at the end of this note: `kev_match.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 kev_match.py findings.json kev.csv
```

**Example output**

```text
HIT CVE-2024-3400 edge-01 due 2024-05-03 900d overdue
SUMMARY 2 findings, 1 KEV, 1 overdue
```

## Explained

### What it does

`kev_match.py` joins a findings export with the CISA KEV catalog. It matches on CVE, pulls vendor, product and the date the entry was added, turns the due date into days remaining, and prints each hit with its deadline. The real CSV needs no editing: the loader reads cveID, vendorProject, product and dueDate.

### What the screen shows

The panel walks two findings and prints HIT CVE-2024-3400 edge-01 due 2024-05-03 900d overdue, then SUMMARY 2 findings, 1 KEV, 1 overdue. A real export prints one HIT line per finding, most overdue first.

### How to run it

`python3 kev_match.py findings.json known_exploited_vulnerabilities.csv --today 2026-10-20`, every weekday before standup. Exit 0 is no match, 1 is at least one, 2 is bad input.

### The fix

A KEV hit is not a debate. Give it an owner, a patch window and a date today; if it cannot be patched, the compensating control needs the same date.

### Prevention

Check KEV at ingest and again daily. Absence is not safety: the catalogue holds exploitation with public evidence, not every exploitation.

> **The honest caveat:** KEV is a floor. Real attacks never get an entry, and the due dates are written for US federal agencies.

> **The lesson:** a severity score is an opinion about impact, and KEV is a record of someone trying.

## In one line

> **Exploited beats scored.** A severity score is an opinion. KEV is a record.

**Check the catalog**

```bash
python3 kev_match.py f.json kev.csv
```

## Script: kev_match.py

Download: [scripts/kev_match.py](../scripts/kev_match.py)

```python
#!/usr/bin/env python3
"""Match findings against the CISA KEV catalog and show the due dates.

Reads a findings export (JSON) and a KEV catalog export (CSV). Prints every
finding whose CVE is listed, with vendor, product, the date it was added, the
remediation due date, and whether that date has passed.

    python3 kev_match.py findings.json known_exploited_vulnerabilities.csv
    python3 kev_match.py findings.json kev.csv --today 2026-10-20

The findings export is a JSON list of objects with a cve field, plus asset,
cvss and package where you have them.

Daily, before the standup:

    30 7 * * 1-5 python3 kev_match.py findings.json kev.csv > kev_today.txt

KEV is a catalog of vulnerabilities with evidence of exploitation in the wild,
published by CISA. Each entry carries a due date for US federal civilian
agencies; for everyone else it is still the best public deadline to copy.

Exit codes: 0 no finding matches KEV, 1 at least one matches, 2 bad input.

By s0sta.com
"""
import argparse
import csv
import datetime
import json
import sys

CVE_COLS = ("cve", "cveid", "cve_id")
VENDOR_COLS = ("vendor", "vendorproject", "vendor_project")
PRODUCT_COLS = ("product",)
ADDED_COLS = ("added", "dateadded", "date_added")
DUE_COLS = ("due", "duedate", "due_date")
RANSOM_COLS = ("ransomware", "knownransomwarecampaignuse")


def die(msg):
    sys.stderr.write("kev_match: %s\n" % msg)
    raise SystemExit(2)


def pick(names, aliases, default):
    for i, name in enumerate(names):
        if name in aliases:
            return i
    return default


def parse_day(text):
    text = (text or "").strip()
    if not text:
        return None
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        return None


def load_findings(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        die("cannot read findings %s: %s" % (path, exc))
    if isinstance(data, dict):
        data = data.get("findings", data.get("results", []))
    if not isinstance(data, list):
        die("findings must be a JSON list, got %s" % type(data).__name__)
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
            "asset": str(f.get("asset", "") or "-"),
            "package": str(f.get("package", "") or "-"),
        })
    return out


def load_kev(path):
    catalog = {}
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError as exc:
        die("cannot read KEV catalog %s: %s" % (path, exc))
    with fh:
        rows = csv.reader(fh)
        header = None
        for row in rows:
            if not row or not any(c.strip() for c in row):
                continue
            if row[0].strip().startswith("#"):
                continue
            names = [c.strip().lower() for c in row]
            if header is None:
                if any(n in CVE_COLS for n in names):
                    header = names
                    continue
                header = []
            if header:
                ic = pick(header, CVE_COLS, 0)
                iv = pick(header, VENDOR_COLS, -1)
                ip = pick(header, PRODUCT_COLS, -1)
                ia = pick(header, ADDED_COLS, -1)
                idu = pick(header, DUE_COLS, -1)
                ir = pick(header, RANSOM_COLS, -1)
            else:
                ic, iv, ip, ia, idu, ir = 0, -1, -1, -1, -1, -1
            if len(row) <= ic:
                continue
            cve = row[ic].strip().upper()
            if not cve.startswith("CVE-"):
                continue

            def cell(i):
                return row[i].strip() if 0 <= i < len(row) else ""

            catalog[cve] = {
                "vendor": cell(iv),
                "product": cell(ip),
                "added": parse_day(cell(ia)),
                "due": parse_day(cell(idu)),
                "ransomware": cell(ir),
            }
    if not catalog:
        die("no CVE entries in KEV catalog %s" % path)
    return catalog


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Match findings against the CISA KEV catalog.")
    ap.add_argument("findings", help="findings export (JSON)")
    ap.add_argument("kev", help="KEV catalog export (CSV)")
    ap.add_argument("--today", help="ISO date to compare due dates with")
    ap.add_argument("--json", action="store_true", help="print JSON, not text")
    args = ap.parse_args(argv)

    today = datetime.date.today()
    if args.today:
        today = parse_day(args.today)
        if today is None:
            die("--today must be an ISO date such as 2026-10-20")

    findings = load_findings(args.findings)
    catalog = load_kev(args.kev)

    hits = []
    for f in findings:
        entry = catalog.get(f["cve"])
        if not entry:
            continue
        row = dict(f)
        row.update({
            "vendor": entry["vendor"],
            "product": entry["product"],
            "added": entry["added"].isoformat() if entry["added"] else "",
            "due": entry["due"].isoformat() if entry["due"] else "",
            "ransomware": entry["ransomware"],
        })
        if entry["due"] is None:
            row["days"] = None
        else:
            row["days"] = (entry["due"] - today).days
        hits.append(row)

    # Most overdue first, then the nearest due date, then unknown dates.
    hits.sort(key=lambda r: (r["days"] is None,
                             r["days"] if r["days"] is not None else 0,
                             r["cve"]))
    overdue = [h for h in hits if h["days"] is not None and h["days"] < 0]

    if args.json:
        print(json.dumps({
            "today": today.isoformat(),
            "counts": {"findings": len(findings), "kev_hits": len(hits),
                       "overdue": len(overdue)},
            "hits": hits,
        }, indent=2, default=str))
        return 1 if hits else 0

    for h in hits:
        name = " ".join(x for x in (h["vendor"], h["product"]) if x) or "-"
        if h["days"] is None:
            when = "due unknown"
        elif h["days"] < 0:
            when = "due %s %dd overdue" % (h["due"], abs(h["days"]))
        elif h["days"] == 0:
            when = "due %s today" % h["due"]
        else:
            when = "due %s in %dd" % (h["due"], h["days"])
        print("HIT %-16s %-10s %-28s added %-10s %s"
              % (h["cve"], h["asset"], name[:28],
                 h["added"] or "-", when))
    print("SUMMARY %d finding%s, %d KEV hit%s, %d overdue as of %s"
          % (len(findings), "" if len(findings) == 1 else "s",
             len(hits), "" if len(hits) == 1 else "s",
             len(overdue), today.isoformat()))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
```
