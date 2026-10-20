---
id: p134
title: "9 git commands to undo mistakes"
slug: 9-git-commands-to-undo-mistakes
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Git, DevOps, VersionControl, SoftwareDevelopment, Programming]
source: "LinkedIn post P134 · IT series"
linkedin_date: 2027-08-05
design: steps
---

# 9 git commands to undo mistakes

The scariest Git moments are almost always recoverable. Nine commands to undo mistakes, from a wrong edit to a commit you thought was gone.

## Quick reference

### Not committed yet — Changes still in the working tree

```bash
# Throw away local changes to one file. It is gone, so be sure.
git restore file.txt
# Unstage a file but keep your edits.
git restore --staged file.txt
# Park all changes to deal with later. git stash pop brings them back.
git stash
```

### Already committed — Fix the last commit or go back

```bash
# Fix the last commit message or add a forgotten file.
git commit --amend
# Undo the last commit, keep the changes staged.
git reset --soft HEAD~1
# Undo a commit by adding an opposite one. Safe when pushed.
git revert <hash>
```

### When it looks lost — The safety nets

```bash
# Every place HEAD has been. Your time machine.
git reflog
# Restore one file from any past commit.
git checkout <hash> -- file
# Pull one commit from another branch to here.
git cherry-pick <hash>
```

## Explained

### Not committed yet

`git restore file.txt` throws away local changes to one file, back to the last commit. The change is gone, so be sure first.  
`git restore --staged file.txt` unstages a file but keeps your edits. The modern replacement for git reset HEAD file.  
`git stash` parks all your uncommitted changes and gives you a clean tree. `git stash` pop brings them back. Perfect when you need to switch branches in a hurry.

### Already committed

`git commit --amend` fixes the most recent commit: a typo in the message, or a file you forgot to add. Only before you push, since it rewrites that commit.  
`git reset --soft HEAD~1` undoes the last commit but keeps the changes staged, ready to recommit differently. `--mixed` keeps them unstaged; `--hard` throws them away.  
`git revert <hash>` undoes a commit by creating a new one that reverses it. This is the safe choice on a shared branch, because it does not rewrite history.

### When it looks lost

`git reflog` shows every position HEAD has had, even commits no longer on any branch. This is how you recover from a bad reset.  
`git checkout <hash> -- file` restores a single file from any past commit without touching anything else.  
`git cherry-pick <hash>` copies one commit from another branch onto your current one.

> **The rule that calms everyone down:** once something is committed, Git keeps it for weeks in the reflog, even if no branch points to it.

## In one line

> **Committed work is rarely lost.** reflog remembers for weeks. Breathe, then recover.

**When you panic**

```bash
git reflog
```
