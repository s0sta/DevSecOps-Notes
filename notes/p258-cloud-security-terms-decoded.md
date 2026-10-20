---
id: p258
title: "Cloud security terms, decoded"
slug: cloud-security-terms-decoded
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [CloudSecurity, AWS, IAM, DevSecOps, CloudNative]
source: "LinkedIn post P258 · Platform series"
linkedin_date: 2028-05-21
design: reveal
---

# Cloud security terms, decoded

Cloud security has a vocabulary problem: the words sound like features, but they are controls. Learn these six and half the architecture diagrams start making sense.

## Quick reference

- **OIDC federation** — A CI job trades a short-lived OIDC token for cloud credentials, so no static key is stored.
- **Workload ID** — A cloud identity bound to a Kubernetes ServiceAccount, so the pod calls the cloud as itself.
- **CIEM** — Cloud Infrastructure Entitlement Management: it maps which identity can do what, and finds unused admin rights.
- **CSPM** — Cloud Security Posture Management: it scans the account for public buckets, open ports and missing logs.
- **Least privilege** — Only the actions a job needs, on only the resources it needs, for only as long as it runs.
- **Break-glass** — A sealed emergency account, kept out of daily use, with every login alerted and reviewed.

## Explained

### Identity

OIDC federation lets a CI job present a signed, short-lived token to the cloud and receive temporary credentials in return. Nothing long-lived sits in the pipeline, which removes the static key that leaks in a log.

Workload identity is the same idea inside Kubernetes: a cloud identity is bound to a ServiceAccount, so a pod calls the cloud as itself, not as the node.

CIEM, Cloud Infrastructure Entitlement Management, maps which identity can do what across accounts, and finds the admin permission nobody uses.

### Posture

CSPM, Cloud Security Posture Management, scans the account for misconfiguration: public buckets, open security groups, disabled logging, unencrypted volumes. It answers what is exposed, not who can reach it.

Least privilege is the rule that ties them together: only the actions a job needs, on only its resources, for only as long as it runs. Permission boundaries enforce it; Access Analyzer finds where it slipped.

### The exception

Break-glass is the account kept for the day normal access fails. It is sealed, out of daily use, with MFA, a vaulted credential and an alert on every login.

> **The honest caveat:** CIEM and CSPM are product categories, not guarantees. Both are only as good as the permissions they can read and the rules someone maintains.

> **The lesson:** the vocabulary is a checklist. Federation, identity, entitlement, posture, least privilege, break-glass.

## In one line

> **Know the term, know the control.** A vocabulary is a checklist you can run.

**Check a role**

```bash
aws iam get-role --role-name api
```
