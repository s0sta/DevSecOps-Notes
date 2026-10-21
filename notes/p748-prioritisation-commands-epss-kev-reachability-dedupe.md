---
id: p748
title: "Prioritisation commands: EPSS, KEV, reachability, dedupe"
slug: prioritisation-commands-epss-kev-reachability-dedupe
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, EPSS, CISAKEV, CommandLine, CyberSecurity]
source: "LinkedIn post P748 · ASM series"
linkedin_date: 2031-07-08
design: cheatsheet
---

# Prioritisation commands: EPSS, KEV, reachability, dedupe

The prioritisation argument is usually an argument about which tool to open. Four blocks answer the four questions in order, and none of them needs a dashboard.

## Quick reference

### EPSS

```bash
zcat epss_scores-current.csv.gz | head
sort -t, -k2 -gr epss.csv | head -20
awk -F, '$2>=0.5' epss.csv
python3 epss_rank.py f.json e.csv --top 5
```

### KEV

```bash
grep -c '^CVE-' kev.csv
grep CVE-2024-3400 kev.csv
csvcut -c cveID,dueDate kev.csv | head
csvsort -c dueDate kev.csv | head
python3 kev_match.py f.json kev.csv
```

### Reachability

```bash
python3 -m modulefinder app.py > graph.txt
grep -i requests graph.txt
grep -rn "import requests" .
python3 -X importtime app.py 2>&1 | tail
python3 reachability_map.py g.json v.txt
```

### Dedupe

```bash
jq -s 'add|unique_by(.cve)' *.json
jq -s 'add|length' *.json
jq -r '.[]|.cve' s1.json | sort | uniq -c
jq -s 'add|group_by(.cve)|length' *.json
python3 finding_dedupe.py s1.json s2.json
```

## Explained

### EPSS

`zcat epss_scores-current.csv.gz | head` shows the export format: a comment line, then cve, epss and percentile. `sort -t, -k2 -gr epss.csv | head -20` ranks your local file by score, and `awk -F, '$2>=0.5' epss.csv` keeps the ones above a half. The last line ranks your own findings.

### KEV

`grep -c '^CVE-' kev.csv` counts CVE entries, `grep CVE-2024-3400 kev.csv` checks one. The catalog quotes any field containing a comma, so cut and `awk -F`, misread column eight; csvcut -c cveID,dueDate kev.csv | head keeps the quoting honest, and csvsort -c dueDate kev.csv | head sorts the catalog by deadline.

### Reachability

`python3 -m modulefinder app.py > graph.txt` writes what a script imports, and `grep -i requests graph.txt` reads it back; `grep -rn "import requests" .` finds direct importers, and `python3 -X importtime app.py 2>&1 | tail` shows what actually loaded at run time. Then the map script turns the graph into reachable or not.

### Dedupe

`jq -s 'add|unique_by(.cve)' *.json` merges by CVE, `jq -s 'add|length' *.json` counts reports before and after, and `jq -r '.[]|.cve' s1.json | sort | uniq -c` shows the worst repeat offenders.

> **The honest caveat:** none of these commands proves exploitation, and the thresholds in them are yours to defend.

> **The lesson:** the queue is a pipeline, and every block is one filter you can check.

## In one line

> **Know the score before the queue.** A number you cannot reproduce is a rumour.

**Start with kev**

```bash
grep -c '^CVE-' kev.csv
```
