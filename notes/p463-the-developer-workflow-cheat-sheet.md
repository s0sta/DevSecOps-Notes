---
id: p463
title: "The developer workflow cheat sheet"
slug: the-developer-workflow-cheat-sheet
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Git, GitHub, DeveloperExperience, DevOps, CommandLine]
source: "LinkedIn post P463 · DevOps series"
linkedin_date: 2029-09-11
design: cheatsheet
---

# The developer workflow cheat sheet

The loop between a thought and a green build is where a working day disappears. These commands shorten it.

## Quick reference

### Worktrees

```bash
git worktree add ../hotfix main
git worktree list
git worktree remove ../hotfix
git worktree add -b fix/412 ../p412
git worktree prune
```

### Review

```bash
gh pr list --state open
gh pr checkout 412
gh pr view 412 --comments
gh pr diff 412 --color=never
gh pr checks 412 --watch
```

### CI locally

```bash
act pull_request
act -j build
act -l
act -n
act --secret-file .secrets
```

### Debug

```bash
tmux new -s debug
tmux attach -t debug
tmux ls
tmux split-window -h
tmux send-keys -t debug 'make test' Enter
```

## Explained

### Worktrees

A worktree is a second checkout of the same repository, so a hotfix does not disturb the branch you were reading. git worktree add puts it beside the main checkout, `git worktree list` shows every tree, git worktree remove clears a finished one, and prune tidies the records. A branch can live in one worktree at a time.

### Review

gh pr list shows the open queue, and `gh pr checkout 412` puts a branch in your working copy without a manual fetch. `gh pr view 412 --comments` reads the discussion, gh pr diff 412 shows the patch, and `gh pr checks 412 --watch` waits for CI in the terminal.

### CI locally

act runs the workflow on your machine in Docker. act pull_request runs the event you care about, act -j build runs one job, act -l lists them, act -n does a dry run, and act `--secret-file .secrets` loads the values CI would inject.

### Debug

`tmux new -s debug` starts a session that survives a dropped connection. Reattach with `tmux attach -t debug`, list sessions with `tmux ls`, split a pane with `tmux split-window -h`, and send a command with `tmux send-keys -t debug 'make test' Enter`. `tmux kill-session -t` debug ends it.

> **The honest caveat:** act is close to Actions, not identical. The runner image, secrets and cache differ, so a green local run is evidence, not proof.

> **The lesson:** the fastest pipeline is the one you can run before you push.

## In one line

> **Fewer tools, sharper loop.** A command you can recall beats a plugin you have to configure.

**Start a worktree**

```bash
git worktree add ../hotfix main
```
