---
id: p428
title: "Trunk-based vs GitFlow"
slug: trunk-based-vs-gitflow
sections: [devsecops]
topic: "Release & build engineering"
tags: [Git, DevOps, ReleaseEngineering, CICD, SoftwareEngineering]
source: "LinkedIn post P428 · DevOps series"
linkedin_date: 2029-06-21
design: compare
---

# Trunk-based vs GitFlow

The branch model argument is about how often code meets main. Trunk-based development merges every day; GitFlow defers the meeting to a release branch.

## Quick reference

| | **TRUNK-BASED** | **GITFLOW** |
|:--|:--|:--|
| Model | One trunk, short PRs | Many long-lived branches |
| Integration | Merged daily to main | Merged at release time |
| Release | A tag on main | A stabilised branch |
| Hotfix | Fix on main, tag again | Branch, then merge twice |
| Merge pain | Small and constant | Large and deferred |
| Best for | Continuous delivery | Versioned, scheduled releases |

**TRUNK-BASED** (One branch, merges every day): Everyone merges to main daily; a release is a tag on main.

```bash
git switch -c feat/sso
```

**GITFLOW** (Long-lived release branches): Develop, release and hotfix branches, each merged twice.

```bash
git flow release start 1.4
```

- Trunk → merge daily, release from one commit.
- GitFlow → stabilise a branch, then merge twice.

## Explained

### The models

Trunk-based: one long-lived branch, short-lived feature branches, and a merge to main at least daily. Releases are cut from a commit on main, usually with a tag. It depends on fast CI and flags, because unfinished work must ship dark safely.

GitFlow: main, develop, feature, release and hotfix branches. Features merge into develop; a release branch is cut and stabilised; main only ever holds what shipped; a hotfix branches from main and merges back into both main and develop.

### What changes

Integration. Trunk-based finds conflicts in hours; GitFlow finds them at release time, when the branch has drifted. Release. A trunk release is a tag on main; a GitFlow release is a branch that receives only fixes. Hotfix. Trunk fixes forward on main and tags again; GitFlow fixes on a hotfix branch and merges twice.

### Choosing

Trunk-based fits continuous delivery, a strong test suite and flags that hide unfinished work. GitFlow fits versioned software with several supported releases, or a cadence that needs a stabilisation window. Most teams adopting GitFlow for a web service keep the branches and lose the cadence.

> **The honest caveat:** GitFlow is not wrong, but it is often chosen for the diagram rather than the release schedule, and long-lived branches make the merge the riskiest event in the quarter.

> **The lesson:** choose the branch model that matches how often you want to integrate, not how the diagram looks.

**Merge daily, or**  
merge in fear.
