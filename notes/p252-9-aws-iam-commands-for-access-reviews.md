---
id: p252
title: "9 AWS IAM commands for access reviews"
slug: 9-aws-iam-commands-for-access-reviews
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [AWS, IAM, CloudSecurity, DevSecOps, CloudComputing]
source: "LinkedIn post P252 · Platform series"
linkedin_date: 2028-05-07
design: terminal
---

# 9 AWS IAM commands for access reviews

An access review ends with a decision about every key, role and policy. Doing it from the console is slow and easy to miss. Nine AWS CLI commands cover the loop, and they change no permissions.

## Quick reference

### Who has access

```bash
# identity and age
aws iam get-user --user-name alice
# long-lived keys
aws iam list-access-keys --user-name alice
# what the user can do
aws iam list-attached-user-policies --user-name alice
```

### What the policy allows

```bash
# the document in force
aws iam get-policy-version --policy-arn $ARN --version-id v3
# every role in the account
aws iam list-roles
# who can assume it
aws iam get-role --role-name deploy-prod
```

### Prove it, then export

```bash
# model one action
aws iam simulate-principal-policy --policy-source-arn $P --action-names s3:GetObject
# every human account
aws iam list-users
# password and MFA status
aws iam generate-credential-report
```

## Explained

### Who

`aws iam get-user --user-name alice` shows the identity and when it was created.  
`aws iam list-access-keys --user-name alice` shows every access key, its status and age. A three-year-old active key is a finding.  
`aws iam list-attached-user-policies --user-name alice` shows the managed policies attached to the user, one part of why alice can do that.

### What

`aws iam get-policy-version --policy-arn $ARN --version-id v3` prints the policy document. Replace v3 with the default version, the one in force.  
`aws iam list-roles` lists roles in the account. The interesting ones trust a human or a wildcard.  
`aws iam get-role --role-name deploy-prod` shows the trust policy, which answers who can assume the role, and the maximum session duration.

### Audit

`aws iam simulate-principal-policy --policy-source-arn $P --action-names s3:GetObject` evaluates one action for one principal. It is a model, not a log: what the policy allows, not what happened.  
`aws iam list-users` lists IAM users, including the ones that should have been deleted.  
`aws iam generate-credential-report` requests the CSV: password age, MFA status and key rotation for every user.

> **The honest caveat:** the credential report is sensitive and takes minutes to generate. Download it with get-credential-report, store it privately and delete it after the review.

> **The lesson:** access reviews are a query, not a meeting.

## In one line

> **Access reviews beat intentions.** Nine commands, one account, before the auditor asks.

**Try it**

```bash
aws iam get-credential-report
```
