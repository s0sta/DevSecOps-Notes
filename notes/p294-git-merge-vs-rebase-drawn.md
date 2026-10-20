---
id: p294
title: "Git merge vs rebase, drawn"
slug: git-merge-vs-rebase-drawn
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Git, VersionControl, DevOps, CICD, SoftwareEngineering]
source: "LinkedIn post P294 · Visual series"
linkedin_date: 2028-08-13
design: explainer
---

# Git merge vs rebase, drawn

A branch is forty commits behind main and the pull request is a zigzag of merge commits. The reviewer asks for a rebase and the argument starts. Four shapes explain what each side means.

## Quick reference

### Fast-forward

- main has not moved since you branched
- Git slides the label forward, no new commit
- History stays linear and unchanged
- Only possible when nothing diverged

### Merge commit

- Both branches keep every commit
- One new commit with two parents
- Conflict resolved once, in the merge
- History shows what actually happened

### Rebase

- Your commits replay on the new base
- New hashes, same changes
- Linear history, no merge commit
- Never rebase what others have pulled

### Squash merge

- Every branch commit becomes one
- Main gets a single tidy change
- The branch history is lost
- Good for a messy feature branch

> **Note:** Rebase your own branch. Merge the shared one. The rule is about who else has the commits.

## Explained

### Fast-forward

If main has not moved since you branched, Git slides the main label forward. No merge commit appears, history stays linear, and your commits land unchanged. The result is indistinguishable from having committed straight to main.

### Merge commit

If both sides moved, git merge main creates one commit with two parents. Every commit survives, the conflict is resolved once, and the history shows what actually happened, mess included.

### Rebase

git rebase main replays your commits on top of main, one at a time. You get linear history and new hashes: the changes are the same, the commits are not. Anyone who already pulled your branch now has different history to reconcile.

### Squash merge

The pull request becomes one commit on main. The feature history disappears, main gets one readable change, and the individual steps are gone, which is sometimes the point. Many teams enable only this button on main, because it keeps the log readable.

> **The honest caveat:** none of these is wrong. Rebasing your own unpushed branch is clean; rebasing a shared one forces everyone else to recover.

> **The lesson:** merge records what happened, rebase edits how it reads. Pick the one your team needs and write it down.

## In one line

> **Rewrite your own. Merge the shared.** The history other people pulled is not yours to rewrite.

**Before you rebase**

```bash
git branch backup && git rebase main
```
