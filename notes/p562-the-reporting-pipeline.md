---
id: p562
title: "The reporting pipeline"
slug: the-reporting-pipeline
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, SecurityReporting, Automation, CICD]
source: "LinkedIn post P562 · PythonSec series"
linkedin_date: 2030-04-30
design: architecture
---

# The reporting pipeline

A scan finishes and the output is three files in three formats. The person who asked for a report gets none of them, and the findings live in a channel nobody owns.

## Quick reference

- **Collect:** Scanner output (SCAN) · Asset inventory (INV)
- **Normalise:** Schema mapping (MAP) · Dedupe key (KEY)
- **Publish:** Report (OUT) · Exit gate (GATE)

**Request flow:** Scanner output → Schema mapping → Dedupe key → Report → Exit gate; Asset inventory → Schema mapping

**Around it:** Exit code (EXIT) · Owner map (OWNER)

## Explained

### Collect

Two inputs, not one. The scanner output is whatever the tool prints: JSON, SARIF or a table in a log. The asset inventory supplies the context the scanner lacks: service, environment and owner. Collect both unchanged before any filtering.

### Normalise

Map every scanner field onto one schema: finding ID, asset, severity, evidence, first seen. Then dedupe on a fingerprint built from the rule and the resource, so the same issue from two tools counts once. A finding that cannot be mapped is logged, not dropped. A missing inventory row is a finding too, because an asset nobody owns cannot be fixed.

### Publish

One report, generated from the normalised rows, and one gate. The report is for people: what changed, what is new, who owns it. The gate is for machines: exit 1 when a new critical appears, so the pipeline stops before the deploy. Both read the same rows, which is why the numbers agree.

> **The honest caveat:** normalisation loses scanner-specific detail. Keep the raw output beside the report, or the first disputed finding sends someone back to the tool.

> **The lesson:** a report is a pipeline, not a document.

## In one line

> **Collect once, publish once.** One schema, one report, one exit code.

**Count the inputs**

```bash
find scans -type f | wc -l
```
