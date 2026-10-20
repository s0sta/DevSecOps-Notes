---
id: p198
title: "How a GitHub Actions workflow is structured"
slug: how-a-github-actions-workflow-is-structured
sections: [devsecops]
topic: "Git & CI/CD"
tags: [GitHubActions, CICD, DevOps, Automation, Git]
source: "LinkedIn post P198 · Cloud / DevSecOps series"
linkedin_date: 2028-01-02
design: stack
---

# How a GitHub Actions workflow is structured

A GitHub Actions workflow looks like a wall of YAML until you see that it is just levels nested inside each other. Here is the structure, top to bottom.

## Quick reference

*Top to bottom: each level contains the next*

1. **Workflow** — One YAML file in .github/workflows. The whole pipeline. · `ci.yml`
2. **Trigger (on:)** — What starts it: push, pull_request, schedule. · `on: push`
3. **Jobs** — Independent units. They run in parallel by default. · `jobs:`
4. **Runner** — The machine each job runs on. A fresh VM every time. · *runs-on*
5. **Steps** — The ordered commands in a job: actions or run. · `steps:`
6. **Actions** — Reusable building blocks, pinned by version. · `uses: @v4`

## Explained

Workflow. One YAML file in .github/workflows/, like `ci.yml`. It is the whole pipeline, and a repo can have many, each for a different purpose: tests, deploys, scheduled jobs.

Trigger (on:). What starts the workflow: a push, a pull_request, a schedule (cron), a manual workflow_dispatch, or an event from another workflow. This is the when.

Jobs. A workflow contains one or more jobs. By default they run in parallel, on separate machines, which is a common surprise. Use needs: to make one job wait for another.

Runner (runs-on:). Each job runs on a runner, a fresh virtual machine such as ubuntu-latest, or a self-hosted one. Fresh means no leftover state from last time, which is why you install dependencies every run.

Steps. Inside a job, steps run in order, top to bottom, on the same runner. A step is either a shell command (run:) or an action (uses:).

Actions. Reusable building blocks that steps call, like actions/checkout to get your code or actions/setup-node to install Node. Pin them to a version (@v4), never @main, so an upstream change cannot break your build.

The nesting in one line: a workflow has jobs, a job runs on a runner and contains steps, and a step can use an action. Once that clicks, reading and writing CI becomes straightforward.

## In one line

> **Workflow, job, step, action.** Know the nesting and the YAML stops being a mystery.

**Start small:** one workflow, one job, a few steps
