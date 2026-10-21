---
id: p423
title: "The git release cheat sheet"
slug: the-git-release-cheat-sheet
sections: [devsecops]
topic: "Release & build engineering"
tags: [Git, ReleaseEngineering, DevOps, CICD, SoftwareEngineering]
source: "LinkedIn post P423 · DevOps series"
linkedin_date: 2029-06-10
design: cheatsheet
---

# The git release cheat sheet

Every release ends with the same four questions: what did we tag, what changed, how do we fix it, and how do we undo it? The commands are short; the order is what people get wrong.

## Quick reference

### Tag

```bash
git tag -a v1.4.0 -m "release 1.4.0"
git tag --list 'v1.*' --sort=-v:refname
git push origin v1.4.0
git show v1.4.0 --stat
git tag -d v1.4.0
```

### Changelog

```bash
git log --pretty=format:%s v1.3.0..v1.4.0
git log --oneline v1.3.0..v1.4.0
git shortlog -sn v1.3.0..v1.4.0
git log --grep='^feat' v1.3.0..v1.4.0
git log --format='%h %s' -n 20
```

### Hotfix

```bash
git switch -c hotfix/1.4.1 v1.4.0
git commit -am "fix: tax rounding"
git tag -a v1.4.1 -m "hotfix 1.4.1"
git push origin hotfix/1.4.1 v1.4.1
git cherry-pick -x 9f2c1ab
```

### Revert

```bash
git revert --no-edit 9f2c1ab
git revert -m 1 4d2e8f0
git revert --no-commit v1.4.0..HEAD
git revert --abort
git log --oneline -5
```

## Explained

### Tag

Annotated tags carry a message and a date; lightweight tags do not. `git tag -a` tags the commit CI passed, git push origin publishes it, and `git tag --sort=-v:refname` lists the newest first.

### Changelog

`git log --pretty=format:'%s'` between two tags prints one subject per commit, which is the raw material for release notes. `--oneline` adds the short hash; shortlog -sn counts contributions per author; `--grep='^feat'` isolates the features. None of them writes the story, but they stop you inventing it.

### Hotfix

Branch from the running tag, not a later main: `git switch -c hotfix/1.4.1 v1.4.0`. Commit the smallest fix, tag it, push the branch and the tag, then merge the fix back so the next release contains it. cherry-pick -x copies a fix and records where it came from.

### Revert

git revert creates a commit that undoes a change, which is safe on a shared branch because history stays intact. For a merge, -m 1 chooses the mainline parent. A range with `--no-commit` lets you read first; `--abort` exits.

> **The honest caveat:** deleting and re-pushing a tag breaks every clone that already fetched it. A tag is a name people pin to, so cut a new patch version instead of moving one.

> **The lesson:** a release cheat sheet is not about typing fast; it is about never guessing which commit is live.

## In one line

> **Tag what shipped, not what might.** The tag is the receipt; the changelog is the story.

**Read the range**

```bash
git log --oneline v1.3.0..v1.4.0
```
