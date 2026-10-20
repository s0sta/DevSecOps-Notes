---
id: p247
title: "A developer's first deploy, hour by hour"
slug: a-developers-first-deploy-hour-by-hour
sections: [devsecops]
topic: "Platform engineering"
tags: [PlatformEngineering, DevOps, GitOps, CICD, Kubernetes]
source: "LinkedIn post P247 · Platform series"
linkedin_date: 2028-04-25
design: timeline
---

# A developer's first deploy, hour by hour

A new developer joins on Monday. By lunch they have a service in production, and nobody opened a ticket. This is what a real golden path buys, hour by hour.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **0:00** | Repo from the template | Clone it. Tests, CI and manifests already exist. |
| **1:00** | First pull request | A small change. The pipeline runs tests, a build and a scan. |
| **2:00** | Staging deploy | Merge to main. Argo CD syncs the staging namespace. |
| **2:30** | First real error | A missing env var. The runbook names the fix, not the person. |
| **3:30** | Promote to production | The same image by tag. No rebuild, no drift. |
| **4:00** | First alert fires | The dashboard and the alert existed before the user did. |

## Explained

### The first hour

Hour zero. They clone the template. The repo already has a test target, CI and manifests for staging and production. The first commit is a one-line change to the README.  
One hour in. They open a pull request. CI runs the tests, builds an image tagged with the commit SHA, and scans it. The pipeline fails on an unpinned dependency: the template teaching the standard, not a reviewer.

### The middle

Two hours in. The merge to main triggers Argo CD. The staging namespace syncs, the pod starts, the health check passes. No kubectl from a laptop.  
Half an hour later. The first real error: a missing environment variable. The pod CrashLoops, the alert fires, and the runbook names the exact secret to add. The fix is a pull request, not a shell command on a running pod.  
Three thirty. The same image is promoted to production by tag. No rebuild: what ran in staging runs in production.

### The last hour

Four hours. The first alert reaches the on-call channel. It is noisy, but real, and the dashboard already shows the four golden signals.

The habit that matters: make the first deploy boring, and every later one inherits the path. The honest caveat: this is a walkthrough, not a stopwatch. The first deploy is fast because the template carries the boring parts, not because production is simple.

## In one line

> **Four hours to first value.** The template carries the boring parts, not the risk.

**Read the runbook**

```bash
cat docs/runbook.md
```
