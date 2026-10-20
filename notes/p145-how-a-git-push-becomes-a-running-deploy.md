---
id: p145
title: "How a git push becomes a running deploy"
slug: how-a-git-push-becomes-a-running-deploy
sections: [devsecops]
topic: "Git & CI/CD"
tags: [CICD, DevOps, Automation, GitOps, CloudComputing]
source: "LinkedIn post P145 · IT series"
linkedin_date: 2027-08-31
design: pipeline
---

# How a git push becomes a running deploy

Between a developer pushing code and that code serving users, a good pipeline does six things automatically. Each step is a gate, so a broken change stops before it reaches customers.

## Quick reference

1. **git push** — You push a branch and open a pull request. · `git push`
2. **CI runs** — Build, tests and linting start automatically. · *CI checks*
3. **Review and merge** — A human approves; the change lands on main. · *merge*
4. **Build the artifact** — CD builds a container image and tags it. · `docker build`
5. **Deploy to staging** — Rolled out, smoke tests run automatically. · *staging*
6. **Promote to production** — Health checks pass, with rollback ready. · *production*

## Explained

1. **git push.** The developer pushes a branch and opens a pull request. This is the trigger for everything that follows, and the last fully manual step.

2. **CI runs.** The moment the PR opens, Continuous Integration kicks off: it builds the project, runs unit and integration tests, and checks formatting and linting. The result is reported back on the pull request as pass or fail. A failed build blocks the merge.

3. **Review and merge.** A teammate reviews the change. Once approved and green, it merges into the main branch. Branch protection rules enforce that nothing reaches main without passing CI and review.

4. **Build the artifact.** Now Continuous Delivery takes over. It builds the deployable artifact, usually a container image, tags it with the commit, and pushes it to a registry. The exact thing that was tested is the thing that ships.

5. **Deploy to staging.** The image rolls out to a staging environment that mirrors production. Smoke tests run automatically to confirm the basics work with real infrastructure.

6. **Promote to production.** With staging green, the image is promoted. A health check watches the rollout, and an automatic rollback stands ready if error rates climb.

The payoff: a fix goes from a laptop to production in minutes, verified at every step. No manual builds, no "works on my machine", no deployment Fridays.

## In one line

> **Code to production, verified at each step.** No manual builds, no deploy Fridays, no guessing.

**Where did it stop?:** check the pipeline, newest run first
