---
id: p462
title: "The developer workflow, drawn"
slug: the-developer-workflow-drawn
sections: [devsecops]
topic: "Platform engineering"
tags: [DevOps, DeveloperExperience, CICD, Git, PlatformEngineering]
source: "LinkedIn post P462 · DevOps series"
linkedin_date: 2029-09-09
design: architecture
---

# The developer workflow, drawn

A change takes three hops before anyone uses it, and each hop has its own clock. The map is the same for a team of two and a platform group of two hundred.

## Quick reference

- **Local · Laptop:** Editor (ED) · Pre-commit hook (HOOK) · Test runner (TEST)
- **Review · Pull request:** Pull request (PR) · CI pipeline (CI) · Reviewer (REV)
- **Ship · Main:** Merge queue (MQ) · Deploy (CD) · Production (PROD)

**Request flow:** Editor → Pre-commit hook → Test runner → Pull request → CI pipeline → Reviewer → Merge queue → Deploy → Production

## Explained

### Local

It starts in the editor, where the change is written. A pre-commit hook runs the fast checks before the commit exists: formatting, secrets, a lint pass. The test runner runs the suite on the laptop, so the first failure costs seconds instead of a queue slot.

### Review

The branch becomes a pull request: diff, description and discussion in one place. The CI pipeline runs the workflow on the branch and reports status checks against the pull request. A reviewer reads the change for intent, not only for green, and asks for a smaller slice when the diff is too large to hold in mind.

### Ship

The merge queue tests the merge result, not the branch alone, so two green pull requests cannot break main together. Deploy takes the merged commit to production, and production is where one clock stops and the next change starts.

> **The honest caveat:** the diagram is a loop, not a line. A failure at deploy sends the work back to the editor, and the review step is usually the slowest hop because it waits for a person.

> **The lesson:** measure each hop separately; an average across all three hides the queue that hurts.

## In one line

> **Fast alone, safe together.** Every tier has to hand off cleanly to the next one.

**Time the handoff**

```bash
gh pr checks 412 --watch
```
