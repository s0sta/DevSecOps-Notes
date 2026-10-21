---
id: p431
title: "Anatomy of a semantic version"
slug: anatomy-of-a-semantic-version
sections: [devsecops]
topic: "Release & build engineering"
tags: [SemVer, ReleaseEngineering, DevOps, Git, SoftwareEngineering]
source: "LinkedIn post P431 · DevOps series"
linkedin_date: 2029-06-28
design: anatomy
---

# Anatomy of a semantic version

A version number is the cheapest API your project has. Package managers, deploy scripts and tired people at two in the morning read it, and it means exactly what SemVer 2.0.0 says it means.

## Quick reference

```text
2.4.1-rc.2+build.7
```

| Part | Name | What it means |
|:--|:--|:--|
| `2.` | Major | Incompatible API change. Increment it, then reset minor and patch. |
| `4.` | Minor | New functionality, backward compatible. The patch number resets. |
| `1` | Patch | Backward-compatible bug fixes, and nothing else. |
| `-rc.2` | Prerelease | Lower precedence than 2.4.1, so resolvers skip it unless asked. |
| `+build.7` | Build metadata | Ignored when comparing versions: it names the build, not the release. |

## Explained

### Major, minor, patch

2 is the major: increment it for an incompatible API change, and reset minor and patch. 4 is the minor: new functionality, backward compatible, with the patch reset. 1 is the patch: backward-compatible bug fixes and nothing else. In 0.y.z the rules relax and anything may change, which is why 1.0.0 is a promise rather than a milestone.

### Prerelease

The `-rc.2` part is a prerelease. It has lower precedence than 2.4.1, so package managers will not choose it unless asked. Dot-separated identifiers compare numerically when they are numbers, so rc.2 is lower than rc.10. That ordering is the point of publishing a candidate before the release.

### Build metadata

The +build.7 part is build metadata. SemVer says it must be ignored when determining precedence, so 2.4.1+build.7 and 2.4.1+build.8 are equal in precedence. It identifies the build; it does not order it.

> **The honest caveat:** SemVer describes the API, not the operation. A config change or a database migration can break production without changing a single endpoint, and no version number will warn you.

> **The lesson:** the number is a contract; change it when the contract changes.

## In one line

> **Break the promise, change the major.** A version number is a contract, not a counter.

**Sort the tags**

```bash
git tag --sort=-v:refname | head -3
```
