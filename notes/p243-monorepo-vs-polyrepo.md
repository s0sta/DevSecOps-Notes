---
id: p243
title: "Monorepo vs polyrepo"
slug: monorepo-vs-polyrepo
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Monorepo, DevOps, CICD, Git, SoftwareEngineering]
source: "LinkedIn post P243 · Platform series"
linkedin_date: 2028-04-16
design: compare
---

# Monorepo vs polyrepo

The monorepo argument is rarely about Git. It is about how often two services must change in the same commit, and what breaks when they cannot.

## Quick reference

| | **MONOREPO** | **POLYREPO** |
|:--|:--|:--|
| Coupling | Atomic across services | Versioned contracts |
| CI speed | Affected-only builds | Small, fast pipelines |
| Tooling | One build system for all | Best tool per repo |
| Ownership | CODEOWNERS per path | A repo per team |
| Versioning | One version for everything | Semver per package |
| Best for | Tightly coupled services | Independent teams |

**MONOREPO** (One repo, one version): One checkout, one CI graph, and a commit that changes API and client together.

```bash
nx affected -t test
```

**POLYREPO** (A repo per service): Each service ships alone, with a versioned package as the contract between them.

```bash
npm i @org/lib@1.4.2
```

- Monorepo → one change, one commit, one CI run.
- Polyrepo → one version per service, released alone.

## Explained

### The trade

Coupling. A monorepo lets one commit change an API and every caller, so CI sees the whole blast radius. A polyrepo puts a versioned package between teams: slower, and much harder to break silently.  
CI speed. A big monorepo is only fast with affected-only builds; Nx, Bazel and Turborepo can build only what changed. Without that graph, every push runs everything and the queue becomes the bottleneck.  
Tooling. One repo means one build system, one lint config and one upgrade path, paid for in migrations. Polyrepos let each team choose, and then let them drift.

### The rest

Ownership. CODEOWNERS maps paths to teams in a monorepo. In a polyrepo the repo boundary is the ownership boundary.  
Versioning. A monorepo usually versions the whole repo together, which is simple until a shared library needs a breaking change. A polyrepo gives each package its own semver and release.  
Best for. Monorepo when services change together and the tooling keeps CI honest. Polyrepo when teams are independent and the contract between them is stable.

> **The honest caveat:** a monorepo without a build graph runs everything on every push, and a polyrepo without version discipline is a dependency maze.

> **The lesson:** choose by coupling, then invest in the tooling that makes it bearable.

## In one line

> **Layout follows coupling, not fashion.** The repo layout should follow how the code changes together.

**See the graph**

```bash
nx graph
```
