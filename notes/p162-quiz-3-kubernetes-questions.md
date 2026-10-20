---
id: p162
title: "Quiz: 3 Kubernetes questions"
slug: quiz-3-kubernetes-questions
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CloudNative, DevOps, InterviewPrep, ITCareer]
source: "LinkedIn post P162 · IT series"
linkedin_date: 2027-10-10
design: quiz
---

# Quiz: 3 Kubernetes questions

Three Kubernetes questions that come up in interviews and in real incidents. Try each before the answer.

## Quick reference

**Q1. A pod is Running but gets no traffic. Most likely cause?**

- a) It is out of memory
- b) Its readiness probe is failing
- c) The node is down

> **Answer:** b) Its readiness probe is failing. Running means the container started. Only pods passing readiness are added to a Service, so a failing probe means no traffic.

**Q2. What does a Deployment actually manage?**

- a) Nodes
- b) ReplicaSets, which manage pods
- c) Services

> **Answer:** b) ReplicaSets, which manage pods. A Deployment creates ReplicaSets, and a ReplicaSet keeps the right number of pods running. Rollouts swap ReplicaSets.

**Q3. Where should you store a database password for a pod?**

- a) In the container image
- b) In a Secret
- c) In the Deployment YAML in git

> **Answer:** b) In a Secret. A Secret keeps it out of the image and the manifest. Back it with a real secrets manager for production.

## Explained

1. A pod is Running but gets no traffic. Most likely cause?

> **Answer:** its readiness probe is failing. Running only means the container process started. A pod receives traffic through a Service, and the Service only sends traffic to pods that pass their readiness probe. So a pod can sit there Running, healthy-looking, and get nothing, because it never reported ready. kubectl get pods shows READY as 0/1 in that case. This one difference explains a huge share of "why is my app not reachable" tickets.

2. **What does a Deployment actually manage?**

> **Answer:** ReplicaSets, which in turn manage pods. You edit a Deployment, it creates a ReplicaSet, and the ReplicaSet keeps the requested number of pods alive. A rolling update works by creating a new ReplicaSet and scaling it up while scaling the old one down. Knowing this explains what you see during kubectl rollout and why old ReplicaSets linger for rollbacks.

3. Where should you store a database password for a pod?

> **Answer:** in a Secret. It keeps the value out of the container image and out of the Deployment YAML you commit to git. On its own a Kubernetes Secret is only base64-encoded, not encrypted, so for production back it with a real secrets manager and enable encryption at rest.

The thread: Running is not the same as ready, and configuration is not the same as secrets.

## In one line

> **Running is not the same as ready.** Most Kubernetes gotchas come back to that difference.

**Check readiness**

```bash
kubectl get pods -o wide
```
