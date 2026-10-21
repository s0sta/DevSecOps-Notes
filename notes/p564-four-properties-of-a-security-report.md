---
id: p564
title: "Four properties of a security report"
slug: four-properties-of-a-security-report
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, SecurityReporting, AppSec, CICD]
source: "LinkedIn post P564 · PythonSec series"
linkedin_date: 2030-05-05
design: explainer
---

# Four properties of a security report

A report that says "3 critical, 12 high" and nothing else is a mood, not a finding. Four properties, checked in this order, separate a report a team can act on from a file nobody opens.

## Quick reference

### Accurate

- Every claim names a file, a line and a command
- No finding without evidence in the same report
- Say what you did not test

### Reproducible

- The reader can rerun every command
- Version, commit and date are pinned
- Fixtures are small and included

### Prioritised

- Severity follows the impact, not the tool
- One critical outranks ten lows
- The first paragraph is the decision

### Owned

- Every finding has a name and a date
- A gate fails the build, not an inbox
- Closed means verified, not filed

> **Note:** Four properties, checked in this order.

## Explained

### Accurate

Every claim names a file, a line and a command. No finding without evidence in the same report. Say what you did not test, because silence reads as coverage. A finding without a reproduction is a hypothesis, and the report should label it.

### Reproducible

The reader can rerun every command. Version, commit and date are pinned. Fixtures are small and included, so the same input gives the same answer next quarter. The artefact digest and the tool version belong in the header, not in a comment.

### Prioritised

Severity follows the impact, not the tool. One critical outranks ten lows. The first paragraph is the decision, so write it as one. A severity that disagrees with the impact teaches the reader to ignore the label.

### Owned

Every finding has a name and a date. A gate fails the build, not an inbox. Closed means verified, not filed. An owner without a date is a name, not a commitment.

> **The honest caveat:** a report can be accurate, reproducible and owned, and still be ignored when the reader disputes the scope. Put the scope on page one.

> **The lesson:** a report is a decision document, not a scan dump.

## In one line

> **A report is a decision.** Four properties turn a scan dump into something a team can act on.

**Ask one owner**

```bash
grep -n 'Owner' report.md
```
