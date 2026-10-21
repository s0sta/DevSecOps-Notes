---
id: p730
title: "9 steps to map your attack surface"
slug: 9-steps-to-map-your-attack-surface
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, AttackSurface, ASM, Python, CloudSecurity]
source: "LinkedIn post P730 · ASM series"
linkedin_date: 2031-05-27
design: steps
---

# 9 steps to map your attack surface

Mapping an attack surface looks like a scanning problem and behaves like a bookkeeping problem. Nine commands, three groups, one order: find what answers, give it a name and an owner, then prove the finding before you close it.

## Quick reference

### Discover — Find what answers first

```bash
# Start at the zone, not the scanner.
dig +short acme.com NS
# Every certificate issued for the name.
curl -s 'https://crt.sh/?q=acme.com'
# Hosts that answer on your own ranges.
nmap -sn 10.0.0.0/24 -oG - | grep Up
```

### Attribute — Give every asset a person

```bash
# Tag owner against CMDB owner.
python3 owner_map.py assets.csv cmdb.csv
# Unknown assets, stale CMDB rows.
python3 shadow_it.py found.csv cmdb.csv
# What the cloud says it owns.
aws resourcegroupstaggingapi get-resources
```

### Verify — Prove it, then close it

```bash
# Suffix match, then the marker.
python3 takeover_check.py dns.csv fp.json
# The record that should not exist.
dig +short blog.acme.com CNAME
# What the target answers today.
curl -sI https://blog.acme.com | head -1
```

## Explained

### Discover

The terminal starts at the zone. `dig +short acme.com NS` names the DNS provider, which is where the records actually live. `curl -s 'https://crt.sh/?q=acme.com'` returns the certificate log, the only inventory that includes names that never resolved. `nmap -sn 10.0.0.0/24 -oG - | grep Up` lists the hosts that answer on your own ranges, which is the part the cloud console forgets.

### Attribute

`python3 owner_map.py assets.csv cmdb.csv` compares the tag owner with the CMDB owner and names the assets with neither. `python3 shadow_it.py found.csv cmdb.csv` reports unknown assets and stale rows with an age, so the ticket has a number. `aws resourcegroupstaggingapi get-resources` is what the cloud says it owns, which is often a shorter list than the bill.

### Verify

`python3 takeover_check.py dns.csv fp.json` matches CNAMEs against fingerprints and confirms the claim page marker. `dig +short blog.acme.com CNAME` is the single record that should not exist. `curl -sI https://blog.acme.com | head -1` is what the target answers today, and that answer is the evidence.

> **The honest caveat:** the loop is weekly, not annual. A surface map older than a quarter describes a company that no longer exists.

> **The lesson:** discover, attribute, verify, and let the exit code decide when the work is done.

## In one line

> **Discover, attribute, then verify.** Three groups, nine commands, one surface map.

**Map it weekly**

```bash
python3 ct_inventory.py ct.json
```
