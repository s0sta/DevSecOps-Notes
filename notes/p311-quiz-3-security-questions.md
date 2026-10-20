---
id: p311
title: "Quiz: 3 security questions"
slug: quiz-3-security-questions
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [CyberSecurity, IAM, Kubernetes, CloudSecurity, DevSecOps]
source: "LinkedIn post P311 · Visual series"
linkedin_date: 2028-09-21
design: quiz
---

# Quiz: 3 security questions

Three questions from the security work in this phase. Answer before you read the reveal. Three answers, each with a control behind it.

## Quick reference

**Q1. What makes s3:\* worse than s3:GetObject on one bucket?**

- a) It is slower for IAM to evaluate.
- b) It grants every call in the service.
- c) It only works from the console.

> **Answer:** b) It grants every call in the service.. s3:\* covers GetObject, PutObject, DeleteObject and PutBucketPolicy. One line can hand over the data and the controls around it, including the bucket policy.

**Q2. What does mTLS prove that a NetworkPolicy does not?**

- a) That the pod runs on the right node.
- b) That both ends hold a trusted certificate.
- c) That the traffic is rate limited.

> **Answer:** b) That both ends hold a trusted certificate.. A NetworkPolicy filters traffic, not identities. mTLS demands a client certificate from a trusted CA, so a compromised pod cannot impersonate the service.

**Q3. Why should every break-glass login page the on-call?**

- a) It has no password.
- b) It bypasses normal access paths by design.
- c) It is shared by the whole team.

> **Answer:** b) It bypasses normal access paths by design.. Break-glass exists for the day the identity provider fails, so its use is rare. A page and a session log make sure the exception is reviewed, not routine.

## Explained

### Question one

What makes s3:\* worse than s3:GetObject on one bucket? It grants every action in the service, not the one call you needed. The wildcard includes GetObject, but also PutObject, DeleteObject and PutBucketPolicy. One line of policy can hand over the data and the controls around it.

### Question two

What does mTLS prove that a NetworkPolicy does not? A NetworkPolicy filters traffic by namespace, pod selector and port. It never authenticates the caller. mTLS requires a certificate from a trusted CA on both ends, so a compromised pod cannot simply claim to be the payments service.

### Question three

Why should every break-glass login page the on-call? The account bypasses the normal access path by design, which is exactly why its use must be reviewed. It is the account an attacker wants, and the one nobody watches.

Each answer is a control. Wildcards are an IAM review, mTLS is an identity check, and break-glass is an alert plus a session log. None of them works without someone reading the result.

> **The honest caveat:** a control you cannot test is a rumour, so run the wildcard query and the handshake yourself.

> **The lesson:** the why is the part that transfers to the next incident.

## In one line

> **Explain the control or remove it.** Three answers and the controls behind them.

**Review one role**

```bash
aws iam list-role-policies --role-name api
```
