---
id: p388
title: "Anatomy of a dependency path"
slug: anatomy-of-a-dependency-path
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SupplyChain, AppSec, NPM, DevSecOps, CyberSecurity]
source: "LinkedIn post P388 · DevSecOps series"
linkedin_date: 2029-03-20
design: anatomy
---

# Anatomy of a dependency path

A scanner reports a critical CVE in a package you have never heard of. Before anyone patches, one question decides the urgency: can the vulnerable code be reached from your application?

## Quick reference

```text
app > express > body-parser > qs > 6.11.0
```

| Part | Name | What it means |
|:--|:--|:--|
| `app` | Your app | The service you ship; the path starts here. |
| `express` | Direct dependency | You chose it and pinned it in `package.json`. |
| `body-parser` | Transitive dep | Express pulls it in; you never named it. |
| `qs` | Vulnerable package | The advisory names this package, not your code. |
| `6.11.0` | Installed version | The exact version the lockfile resolves today. |

## Explained

### The path

The path starts at app, your application: the service you ship. Everything after this point is code you did not write, running with the permissions you gave it.

Next is express, your direct dependency, the package you chose and pinned in `package.json`. You asked for it, you upgrade it, and its release notes are yours to read.

Then body-parser, a transitive dependency pulled in by express. You never named it, never reviewed it, and probably cannot say which version is installed without asking the lockfile.

### The finding

qs is the vulnerable package, where the advisory lands. The CVE names this package and a version range, not your application, which is why the first alert feels remote and the eventual patch feels urgent.

6.11.0 is the installed version, the one the lockfile resolves today. Change one line in the lockfile or one range in `package.json` and the whole path changes, which is why the path is the unit of triage, not the package name.

> **The honest caveat:** a path proves the package is installed, not that the vulnerable function is called. `npm ls qs` shows the tree; only a trace or a code search shows whether the bad branch runs.

> **The lesson:** triage the path, not the package, and patch the version that actually resolves.

## In one line

> **A CVE needs a path to run.** A finding on a package is only a risk if the path reaches it.

**Trace the path**

```bash
npm ls qs
```
