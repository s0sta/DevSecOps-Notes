---
id: p261
title: "Quiz: 3 cloud security questions"
slug: quiz-3-cloud-security-questions
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [CloudSecurity, IAM, AWS, DevSecOps, CloudNative]
source: "LinkedIn post P261 · Platform series"
linkedin_date: 2028-05-28
design: quiz
---

# Quiz: 3 cloud security questions

Three questions from the cloud security work in this phase. Answer before the reveal.

## Quick reference

**Q1. Why is a wildcard action like s3:\* riskier than it looks?**

- a) It is slower to evaluate.
- b) It grants every call in that service.
- c) It only works in the console.

> **Answer:** b) It grants every call in that service.. s3:\* covers GetObject, DeleteObject and PutBucketPolicy. One line grants the whole service, including the calls that destroy data.

**Q2. What does workload identity remove from a CI pipeline?**

- a) The need for a cluster.
- b) Long-lived static cloud keys.
- c) The need for a build step.

> **Answer:** b) Long-lived static cloud keys.. The pipeline presents a short-lived OIDC token, the cloud returns temporary credentials, and no access key sits in a secret store.

**Q3. Why should a break-glass account be audited and alerted?**

- a) It is the only account with MFA.
- b) It bypasses normal access paths by design.
- c) It costs more than a normal role.

> **Answer:** b) It bypasses normal access paths by design.. Break-glass exists for the day normal access fails. Every use should page someone and be reviewed, because it is the account an attacker wants.

## Explained

### Question one

Why is a wildcard action such as s3:\* riskier than it looks? It grants every call in the service, not the one call you needed. s3:\* includes GetObject, but also DeleteObject, PutBucketPolicy and DeleteBucket. One line of policy can hand over the data and the controls around it.

### Question two

What does workload identity remove from a CI pipeline? The long-lived static key. The pipeline presents a short-lived OIDC token, the cloud exchanges it for temporary credentials, and no access key sits in a secret store waiting to leak. That is what OIDC federation and workload identity give you.

### Question three

Why should a break-glass account be audited and alerted? It bypasses the normal access path by design. It exists for the day the identity provider fails, so every use should page someone, log the session and be reviewed afterwards. It is the account an attacker wants most.

Each answer is a control you can check. Wildcard actions are an IAM review. Static keys are replaced by an OIDC trust policy. Break-glass is an alert and a session log.

> **The honest caveat:** knowing the answer is not the same as enforcing it. Check your own account before you grade someone else's.

> **The lesson:** the why is the part that transfers to the next incident.

## In one line

> **Know the why, not the word.** Three answers that outlast the exam.

**Review one role**

```bash
aws iam list-role-policies --role-name api
```
