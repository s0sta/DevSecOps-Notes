---
id: p132
title: "Quiz: 3 Git questions every developer should know"
slug: quiz-3-git-questions-every-developer-should-know
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Git, DevOps, SoftwareDevelopment, VersionControl, ITCareer]
source: "LinkedIn post P132 · IT series"
linkedin_date: 2027-08-01
design: quiz
---

# Quiz: 3 Git questions every developer should know

Three Git questions that separate people who memorised commands from people who understand Git. Try each before reading on.

## Quick reference

**Q1. You committed to the wrong branch. Nothing is pushed yet. Best fix?**

- a) `git reset --hard`, then redo it
- b) `git switch -c right-branch` (moves the commit)
- c) Delete the folder and clone again

> **Answer:** b) `git switch -c right-branch` (moves the commit). Branching from where you are keeps the commit, then reset the old branch. `--hard` would throw the work away.

**Q2. What is the difference between git reset and git revert?**

- a) Nothing, they are aliases
- b) reset moves the branch pointer; revert adds an undo commit
- c) revert deletes history

> **Answer:** b) reset moves the branch pointer; revert adds an undo commit. revert is safe on shared branches: it adds a new commit that undoes the old one. reset rewrites history.

**Q3. git pull is shorthand for which two commands?**

- a) git fetch + git merge
- b) git clone + git checkout
- c) git add + git commit

> **Answer:** a) git fetch + git merge. git pull fetches the remote changes, then merges (or rebases) them. Knowing that explains most pull surprises.

## Explained

1. You committed to the wrong branch, nothing is pushed yet. Best fix?

> **Answer:** create the correct branch from where you are, then move the old branch back. `git switch -c right-branch` keeps your commit, then git switch main and `git reset --hard origin/main` cleans the branch you were on. Reaching straight for `git reset --hard` throws the work away before you have saved it anywhere.

2. What is the difference between git reset and git revert?

> **Answer:** reset moves the branch pointer, rewriting history. revert adds a new commit that undoes a previous one, leaving history intact. On a shared branch, use revert, because rewriting history that others have already pulled causes painful conflicts. On your own local work, reset is fine.

3. git pull is shorthand for which two commands?

> **Answer:** git fetch followed by git merge, or a rebase if you configure it. Fetch downloads the remote changes, merge combines them with yours. This is why an unexpected merge commit or conflict appears after a pull: it is the merge step doing its job. git fetch first, then look, then merge, gives you more control.

The common thread: Git almost never truly loses committed work. git reflog remembers where every branch has been for weeks, so even a bad reset can usually be undone.

## In one line

> **Git rewards those who understand it.** Most scary Git moments are undoable once you know how.

**See what changed**

```bash
git status && git log --oneline -5
```
