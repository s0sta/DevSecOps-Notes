---
id: p467
title: "Anatomy of a commit message"
slug: anatomy-of-a-commit-message
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Git, ConventionalCommits, CodeReview, DevOps, SoftwareEngineering]
source: "LinkedIn post P467 · DevOps series"
linkedin_date: 2029-09-20
design: anatomy
---

# Anatomy of a commit message

A commit message is read twice: by a reviewer in a hurry, and by a tool with no context. The line either gives both what they need or makes them guess.

## Quick reference

```text
fix(api)!: reject expired tokens (#412)
```

| Part | Name | What it means |
|:--|:--|:--|
| `fix` | The type | The kind of change: fix, feat, docs, refactor, perf or test. |
| `(api)` | The scope | The area, in brackets. Optional, one noun, not a file name. |
| `!` | Breaking marker | Sits before the colon. The footer must explain the migration. |
| `: reject expired tokens` | The summary | Imperative, lower case, no full stop: what the change does. |
| `(#412)` | PR reference | GitHub appends it on squash merge; you rarely type it. |

## Explained

### The type

fix is the type: what kind of change this is. feat, docs, refactor, perf, test, build, ci and chore are the other common ones. The type is what a changelog groups by, so a fix filed as chore disappears from the release notes.

### The scope

(api) is the scope: the area of the codebase, not the file name. It is optional, and a new joiner should find it in the layout. One scope per commit is enough; a commit that touches three areas is usually three commits.

### The breaking marker

! is the breaking marker. It goes after the type or scope and before the colon, and it warns every consumer that the next release may break them. The marker starts the conversation; the BREAKING CHANGE footer must explain the migration, or the warning is noise.

### The summary and the reference

: reject expired tokens is the summary: imperative mood, lower case, no full stop, and what the change does, not what you felt. The trailing pull request reference, 412 in the example, is appended by GitHub on squash merge, so you rarely type it.

> **The honest caveat:** Conventional Commits is a convention, not a standard, and nothing enforces the truth of a type. Lint the format in CI, review the meaning by hand.

> **The lesson:** the message is the only part of the change that survives the review.

## In one line

> **A message is a contract.** Read by humans first, tooling second.

**Show the change**

```bash
git show --stat HEAD
```
