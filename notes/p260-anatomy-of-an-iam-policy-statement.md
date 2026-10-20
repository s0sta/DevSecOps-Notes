---
id: p260
title: "Anatomy of an IAM policy statement"
slug: anatomy-of-an-iam-policy-statement
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [AWS, IAM, CloudSecurity, DevSecOps, CloudNative]
source: "LinkedIn post P260 · Platform series"
linkedin_date: 2028-05-25
design: anatomy
---

# Anatomy of an IAM policy statement

An IAM policy is a JSON document, but the behaviour comes from six fields. Read them in order and a policy stops being a wall of text.

## Quick reference

```text
"Sid" "Effect" "Principal" "Action" "Resource" "Condition"
```

| Part | Name | What it means |
|:--|:--|:--|
| `"Sid"` | Statement ID | Optional label for one statement, so a review can point at it. |
| `"Effect"` | Allow or Deny | Allow or Deny. An explicit Deny always wins over any Allow. |
| `"Principal"` | Who | Who it applies to: account, role, user or federated identity. Resource-based policies only. |
| `"Action"` | What | The API calls allowed or denied, like s3:GetObject. A wildcard widens it fast. |
| `"Resource"` | Which thing | The ARN the action applies to. \* means every resource in the account. |
| `"Condition"` | When | Optional tests: MFA present, source IP, tag, VPC endpoint. They narrow a grant. |

## Explained

### The six fields

Sid is an optional statement ID. It changes nothing, but gives reviews a name to point at.

Effect is Allow or Deny, and it is case-sensitive. An explicit Deny always wins over any Allow. A guardrail policy can therefore override an admin grant.

Principal is who the statement applies to: an account, role, user, federated identity or service. It appears in resource-based policies and role trust policies. An identity policy has no Principal because the identity owns the policy.

Action is the API call, written service:operation, like s3:GetObject. It accepts wildcards: s3:\* is every S3 call. List actions explicitly unless you mean the service.

Resource is the ARN it applies to. \* means every resource, and some actions only work with \*. Scope by ARN where possible.

Condition is the when: MFA present, source IP, a tag, a VPC endpoint. All conditions must pass; several values for one key are ORed. A wildcard with a tight Condition is narrower than it looks.

### The version

The Version field at the top, 2012-10-17 in current policies, tells IAM which grammar to parse, not when the policy was created.

> **The honest caveat:** this statement is one layer. Permissions boundaries, SCPs and session policies can remove what it allows, and an explicit Deny anywhere still wins.

> **The lesson:** read the six fields, then ask what the policy does not say.

## In one line

> **Read the fields, not the name.** A policy called ReadOnly can still allow s3:\*.

**Dump the account**

```bash
aws iam get-account-authorization-details
```
