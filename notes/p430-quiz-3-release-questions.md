---
id: p430
title: "Quiz: 3 release questions"
slug: quiz-3-release-questions
sections: [devsecops]
topic: "Release & build engineering"
tags: [DevOps, ReleaseEngineering, CICD, Git, FeatureFlags]
source: "LinkedIn post P430 · DevOps series"
linkedin_date: 2029-06-26
design: quiz
---

# Quiz: 3 release questions

Three questions separate a team that deploys from a team that releases. Answer before the reveal.

## Quick reference

**Q1. Why build once and promote the same artefact through every environment?**

- a) So staging tests the exact production digest
- b) Because rebuilding is slower than promoting
- c) Because registries charge per build

> **Answer:** a) So staging tests the exact production digest. A rebuild can resolve a different base image or dependency, so the digest changes and the tests no longer describe what ships. Promotion moves one digest.

**Q2. What does a merge queue guarantee before a pull request reaches main?**

- a) That every reviewer has approved it
- b) That it passes CI against the latest main
- c) That it deploys to production immediately

> **Answer:** b) That it passes CI against the latest main. The queue builds the pull request on top of the current main, in order, so two green pull requests cannot break main together. Review approval is a separate gate.

**Q3. Why is a feature flag not a deployment?**

- a) It deploys code without a pipeline
- b) It replaces the need for rollback
- c) It changes the code path, not the artefact

> **Answer:** c) It changes the code path, not the artefact. Deploying puts code on the servers; the flag decides who reaches it. That separation lets you ship dark, ramp traffic and kill a feature without a rollback.

## Explained

### The artefact

What does "build once and promote" actually protect? A rebuild is a new artefact. It can resolve a different base image, a newer dependency or a different compiler, and the digest changes. The moment it changes, staging tested something production will never run. Promotion moves the same digest, so the test result still describes the release.

### The queue

What does a merge queue guarantee? That the pull request passed CI on top of the current main, in the order it will merge. Two pull requests can each be green alone and broken together; the queue builds the combination before it lands. It does not guarantee review, and it does not deploy anything.

### The flag

Why is a feature flag not a deployment? Deploying puts code on the servers. The flag decides who reaches it. That separation lets you ship dark, ramp a percentage and kill a feature without a rollback, while the artefact stays exactly the same. A flag is a release control, not a deployment mechanism.

> **The honest caveat:** a merge queue serialises merges, so a busy repository can wait. The guarantee is a green main, not a fast one.

> **The lesson:** deploy is mechanical; release is a decision, and you can reverse it.

## In one line

> **Deploy is not release.** Three answers that separate a pipeline from a release process.

**Check the range**

```bash
git log --oneline v1.4.0..HEAD
```
