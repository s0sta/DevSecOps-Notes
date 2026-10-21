---
id: p439
title: "Make vs Bazel vs Nx"
slug: make-vs-bazel-vs-nx
sections: [devsecops]
topic: "Release & build engineering"
tags: [BuildSystems, Bazel, Nx, DevOps, Monorepo]
source: "LinkedIn post P439 · DevOps series"
linkedin_date: 2029-07-17
design: matrix
---

# Make vs Bazel vs Nx

Make, Bazel and Nx are not three versions of the same tool. They disagree about what a build even is.

## Quick reference

| | **Make** | **Bazel** | **Nx** |
|:--|:--|:--|:--|
| Model | File timestamps | Content hashes | Task graph |
| Caching | None built in | Local + remote | Local + remote |
| Incremental | Per file, by mtime | Action-level | Task-level |
| Ecosystem | Everywhere | JVM, C++, Go, JS | JS/TS plus plugins |
| Learning curve | An afternoon | Weeks | Days |
| Best for | Small native trees | Polyglot monorepos | JS monorepos |

**How to pick**

- **Make** → the default for a small tree.
- **Bazel** → pay the setup once, cache everything.
- **Nx** → the JS monorepo answer, with a graph.

## Explained

### The model

Make is a set of file rules: a target depends on prerequisites, and the timestamp decides. Bazel is an action graph over content hashes: every action declares its inputs and outputs, and the hash decides. Nx is a task graph over projects: it knows which tasks depend on which, and which projects a change touches.

### Cache and incrementality

Make has no cache; it has mtimes, so touching a file rebuilds its targets. Bazel caches action results locally and remotely, keyed by the inputs and the command. Nx caches task results, locally and on Nx Cloud, and replays them for an unchanged project. Incrementality is per file for Make, per action for Bazel and per task for Nx.

### Ecosystem and effort

Make is everywhere and takes an afternoon to learn. Bazel covers JVM, C++, Go and JavaScript, and costs weeks before a large monorepo pays it back. Nx is JavaScript and TypeScript first, with plugins for other stacks, and a team is productive in days. Small native trees stay on Make, polyglot monorepos go to Bazel, and JS monorepos go to Nx.

> **The honest caveat:** Bazel's remote cache needs a server and a genuinely hermetic build, and Nx's remote cache is an Nx Cloud feature. Neither is free to run, and a cache nobody can clear is a liability.

> **The lesson:** pick the graph you can explain, then the cache that fits it.

## In one line

> **Pick the graph, not the logo.** The build tool you can debug at 2 a.m. is the fast one.

**List the targets**

```bash
bazel query 'kind(rule, //...)'
```
