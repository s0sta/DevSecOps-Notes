---
id: p651
title: "Quiz: 3 deploy questions"
slug: quiz-3-deploy-questions
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Bash, Kubernetes, DevOps, SRE, CICD]
source: "LinkedIn post P651 · ShellSec series"
linkedin_date: 2030-11-24
design: quiz
---

# Quiz: 3 deploy questions

Three questions close the deploy phase. Each one is a decision the gate makes for you, and each wrong answer is a failure mode from the previous nine posts in this phase.

## Quick reference

**Q1. Why rehearse a rollback before you need one?**

- a) It proves the undo target exists
- b) It makes the undo faster at 3 a.m.
- c) kubectl requires a rehearsal first

> **Answer:** a) It proves the undo target exists. A dry-run reads the rollout history and prints the command while the cluster is calm. It catches a zero revisionHistoryLimit or a pruned ReplicaSet.

**Q2. What must a smoke test assert after a deploy?**

- a) Status code and a body marker
- b) That the pod restarted
- c) That the pipeline went green

> **Answer:** a) Status code and a body marker. A 200 from a process that is still warming proves little. Assert the status and a string that only a working release returns, on an endpoint that matters.

**Q3. Why is the context check the first gate?**

- a) Wrong cluster, every check is moot
- b) It is the fastest kubectl call
- c) kubectl refuses other contexts

> **Answer:** a) Wrong cluster, every check is moot. The other gates ask the cluster that kubectl is pointed at. If that is staging, a pass means staging is healthy and production stays behind.

## Explained

### Question one

Why rehearse a rollback before you need it? Because a dry-run reads the rollout history and prints the command while the cluster is calm. It finds a zero revisionHistoryLimit or a pruned ReplicaSet before an incident does. The undo target is configuration, and configuration is testable.

### Question two

What must a smoke test assert? The status code and a body marker on an endpoint that matters. A 200 from /health proves the process is listening, not that the release works. A retry can turn a flapping service into a pass, so log the attempts and make a failure fail the build, not open a ticket.

### Question three

Why is the context check first? Because a wrong cluster makes every later check meaningless. The namespace, rollout and digest checks all ask the cluster that kubectl is pointed at; if that is staging, a pass says staging is healthy. The first check decides which cluster the answer belongs to.

> **The honest caveat:** passing this quiz does not make a deploy safe; the gate does.

> **The lesson:** a gate is only as good as its last no.

## In one line

> **A gate is only as good as its no.** The gate is the last post's, and this is the test.

**Run the gate:** `deploy_gate.sh` prod-eu api api
