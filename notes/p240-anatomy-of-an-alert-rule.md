---
id: p240
title: "Anatomy of an alert rule"
slug: anatomy-of-an-alert-rule
sections: [devsecops]
topic: "Observability & SRE"
tags: [Prometheus, Alerting, SRE, DevOps, CloudNative]
source: "LinkedIn post P240 · Platform series"
linkedin_date: 2028-04-09
design: anatomy
---

# Anatomy of an alert rule

A Prometheus alert rule has six fields that matter, and most bad pages come from two of them: for: and labels.

## Quick reference

```text
alert: expr: for: labels: annotations: runbook_url:
```

| Part | Name | What it means |
|:--|:--|:--|
| `alert:` | The name | A short name, e.g. HighErrorRate. |
| `expr:` | The query | Any PromQL vector: results mean it is true. |
| `for:` | The delay | True this long before firing. Stops flapping. |
| `labels:` | The routing | Route and group on these. severity: page. |
| `annotations:` | The message | summary one line, description with numbers. |
| `runbook_url:` | The link | A convention in annotations, not a field. |

## Explained

### What fires

Three fields decide whether the rule fires at all.  
alert: is the name. It becomes the alertname label and the first word on the phone, so make it specific.  
expr: is the query. Any PromQL that returns a vector; the rule fires while that vector has results. One clear ratio beats a compound condition.  
for: is the delay. The expression must stay true for the whole duration before it fires. This is what stops one spike paging anyone.

### Who hears it

labels: route it. severity: page or severity: ticket is a convention, not a reserved word, and Alertmanager routes and groups on it.  
annotations: explain it. summary is the one-liner, description carries the numbers, and both can use {{ $labels.instance }} and {{ $value }}.  
runbook_url: is the link. Not a Prometheus field, a convention inside annotations, and the first thing on-call should click.  
An alert with none of these is a text from a stranger: it says something broke and leaves you to guess what.

> **The honest caveat:** for: delays the page, it does not make it correct. A bad expression with a long for: is still a bad expression.

> **The lesson:** write the rule for the person who gets woken, not for the query editor.

## In one line

> **A rule is a promise to wake up.** Write it for the person who gets the page at 3 a.m.

**Check it first**

```bash
promtool check rules alert.yml
```
