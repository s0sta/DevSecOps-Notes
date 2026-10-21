---
id: p533
title: "The SBOM and licence cheat sheet"
slug: the-sbom-and-licence-cheat-sheet
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SBOM, SupplyChain, Security, DevOps, Python]
source: "LinkedIn post P533 · PythonSec series"
linkedin_date: 2030-02-21
design: cheatsheet
---

# The SBOM and licence cheat sheet

A dependency review arrives as a spreadsheet, a Slack thread and a PDF, and nobody agrees on the package list. Four blocks of commands settle it.

## Quick reference

### Generate

```bash
syft dir:. -o cyclonedx-json
syft registry:app:1.4 -o spdx-json
syft scan dir:. -o table
trivy fs -f cyclonedx -o sbom.json .
```

### Scan

```bash
grype sbom:sbom.json
grype sbom:sbom.json --fail-on high
trivy sbom sbom.json
trivy image --scanners vuln app:1.4
```

### Licences

```bash
pip-licenses --format=json
pip-licenses --format=csv --with-urls
pip-licenses --allow-only="MIT"
trivy fs --scanners license .
```

### Compare

```bash
diff <(jq . a.json) <(jq . b.json)
jq '.components|length' sbom.json
jq -r '.components[].name' s.json|sort
python3 Scripts/sbom_diff.py a b
```

## Explained

### Generate

`syft dir:. -o cyclonedx-json` reads the working tree and writes CycloneDX. `syft registry:app:1.4 -o spdx-json` reads the image that actually ships. `syft scan dir:. -o table` is the quick human view, and `trivy fs -f cyclonedx -o sbom.json .` writes the same shape from the scanner you already run.

### Scan

A scan needs a target. `grype sbom:sbom.json` matches the file against its vulnerability database. Adding `--fail-on` high turns a finding into a failed job. `trivy sbom sbom.json` does the equivalent, and `trivy image --scanners vuln app:1.4` scans the image directly when no SBOM exists yet.

### Licences

pip-licenses `--format=json` dumps the licence of every installed package. `--format=csv --with-urls` adds the project URL a reviewer will ask for. `--allow-only="MIT"` fails the run when something else appears, and `trivy fs --scanners license .` does a similar pass over a directory.

### Compare

Two SBOMs compare line by line. diff <(jq . `a.json`) <(jq . `b.json`) is the first look. `jq '.components|length' sbom.json` counts components, `jq -r '.components[].name' s.json|sort` lists them, and `python3 Scripts/sbom_diff.py a b` adds version changes and an exit code.

> **The honest caveat:** every scanner has its own database and its own idea of a component, so two tools can disagree on the same image. Pick one as the gate and use the other as a second opinion.

> **The lesson:** ask one question per block, and let the exit code end the argument.

## In one line

> **Inventory first, then argue.** Four commands per question, and one exit code.

**Write the sbom**

```bash
syft dir:. -o cyclonedx-json
```
