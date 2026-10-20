---
id: p155
title: "9 git commands for reading history"
slug: 9-git-commands-for-reading-history
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Git, DevOps, VersionControl, Debugging, SoftwareDevelopment]
source: "LinkedIn post P155 · IT series"
linkedin_date: 2027-09-23
design: terminal
---

# 9 git commands for reading history

Git history is not just a record, it is a debugging tool. When something breaks, the answer to "when did this change and why" is a few commands away.

## Quick reference

### See what happened

```bash
# a compact, readable history
git log --oneline -10
# branches and merges, drawn as a tree
git log --oneline --graph --all
# filter by time and author
git log --since='1 week ago' --author=sara
```

### Track down a line

```bash
# who last changed each line, and when
git blame app.py
# the full diff of one commit
git show a1b2c3d
# the history of one file, with diffs
git log -p -- app.py
```

### Search the past

```bash
# find the commit that added or removed a string
git log -S 'apply_coupon'
# commits on feature that are not on main
git log --oneline main..feature
# binary-search history to find a bug
git bisect start
```

## Explained

### See what happened

`git log --oneline -10` gives a compact, readable list of recent commits. Far easier to scan than the full log.  
`git log --oneline --graph --all` draws branches and merges as a tree, so you can see how work came together. The clearest picture of a messy history.  
`git log --since='1 week ago' --author=sara` filters by time and person. Useful for "what changed before this started failing".

### Who and why

`git blame app.py` shows who last changed each line and in which commit. Not for blame in the human sense, but for context: find the commit, then read why it was made.  
git show \<hash> displays one commit in full, message and diff. The natural next step after blame hands you a hash.  
`git log -p -- app.py` shows the history of a single file, each change with its diff. The story of how one file became what it is.

### Find it

`git log -S 'apply_coupon'` finds the commit that added or removed that string. Perfect for "where did this function come from, or go?"  
git log main..feature lists commits on one branch that are not on another. Exactly what a pull request contains.  
`git bisect start` begins a binary search through history. You mark a known-good and known-bad commit, and Git checks out the midpoint repeatedly until it finds the commit that introduced a bug. Powerful on long histories.

## In one line

> **History is a debugging tool.** The commit that introduced a bug is a few commands away.

**Try it**

```bash
git log --oneline --graph --all
```
