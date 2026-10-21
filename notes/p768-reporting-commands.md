---
id: p768
title: "Reporting commands"
slug: reporting-commands
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [Python, VulnerabilityManagement, CommandLine, CyberSecurity, DevOps]
source: "LinkedIn post P768 · ASM series"
linkedin_date: 2031-08-24
design: cheatsheet
---

# Reporting commands

The board pack is due and the numbers live in four files. The commands are short enough to put in a Monday job.

## Quick reference

### Trend

```bash
python3 trend_report.py history.json
jq '.[].opened - .closed' history.json
jq -r '.[-1].date' history.json
python3 trend_report.py h.json --drop 3
```

### Coverage

```bash
python3 coverage_report.py inv scans
jq -r '.[].asset' inv.json | sort -u
jq -r '.[].asset' scans.json | sort -u
jq -r '.[].tool' scans.json | sort -u
```

### Controls

```bash
python3 control_map.py f.json soc2.json
jq -r '.controls | keys[]' soc2.json
jq -r '.[].category' f.json | sort -u
jq -r '.controls[][]' soc2.json | sort -u
```

### Evidence

```bash
sha256sum evidence/* > manifest.txt
grep -c '^FILE ' packet.txt
tar --sort=name -cf packet.tar evidence/
gpg --verify packet.tar.sig packet.tar
```

## Explained

### Trend

`trend_report.py` prints net flow and the closure rate with its denominator. The jq lines pull the flows and the latest date, and `--drop` tightens the line.

### Coverage

`coverage_report.py` joins inventory to scans; the jq lines list assets and tools. A gap list is only useful when the inventory is the population.

### Controls

`control_map.py` maps categories to SOC 2 ids; jq lists the categories and the ids. A finding with no id is a finding the auditor cannot file.

### Evidence

`audit_packet.py` prints the manifest and the per-control index. sha256sum and tar seal the files, grep counts the manifest lines, and gpg verifies the signature. The packet is printed, so redirect it.

### The fix

Run the sheet at the start of the review and paste the output into the pack. Each command answers one question with a number.

### Prevention

Keep the sheet beside the report job and update it when a column changes. A sheet nobody edits becomes a museum of last year's paths.

> **The honest caveat:** the file names are placeholders, and the commands assume jq, GNU tar and gpg are installed. Substitute your paths before you trust the output.

> **The lesson:** a report you can rerun is a control; one you rebuild by hand is a screenshot.

## In one line

> **Run the report, not the meeting.** A command you can rerun beats a number you rebuilt by hand.

**Run the sheet**

```bash
python3 coverage_report.py inv scans
```
