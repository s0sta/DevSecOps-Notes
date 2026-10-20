---
id: p308
title: "The AWS security cheat sheet"
slug: the-aws-security-cheat-sheet
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [AWS, CloudSecurity, IAM, DevSecOps, CloudNative]
source: "LinkedIn post P308 · Visual series"
linkedin_date: 2028-09-14
design: cheatsheet
---

# The AWS security cheat sheet

An alert fires at 02:00, and the first question is not what happened but who did it and with which key. Five commands per area take you from alert to evidence.

## Quick reference

### Identity

```bash
aws sts get-caller-identity
aws iam list-access-keys
aws iam list-mfa-devices --user-name bob
aws iam get-account-password-policy
aws iam get-account-summary
```

### Keys

```bash
aws kms list-keys
aws kms describe-key --key-id $KEY_ID
aws kms list-aliases --output table
aws kms enable-key-rotation --key-id $ID
aws kms list-grants --key-id $KEY_ID
```

### Detection

```bash
aws guardduty list-detectors
aws securityhub get-findings
aws cloudtrail lookup-events --max-items 5
aws cloudtrail describe-trails
aws cloudtrail get-trail-status --name $T
```

### Policy

```bash
aws iam simulate-principal-policy
aws iam get-policy --policy-arn $A
aws iam list-policies --scope Local
aws iam get-role --role-name api
aws iam list-role-policies --role-name x
```

## Explained

### Identity

`aws sts get-caller-identity` tells you which principal the shell is using, which is often not the one you think. list-access-keys and list-mfa-devices show the credentials attached to a user. get-account-password-policy shows the account rules, and get-account-summary gives the quotas and counts.

### Keys

kms list-keys lists the key IDs, and describe-key shows the key manager and the state. list-aliases maps those IDs to names. enable-key-rotation turns annual rotation on for a symmetric customer managed key, and list-grants shows who else has access.

### Detection

guardduty list-detectors finds the detector IDs, and securityhub get-findings pulls the aggregated findings. cloudtrail lookup-events answers what was called recently; describe-trails and get-trail-status prove logging is on and current. If the trail is off, every other answer is a guess.

### Policy

simulate-principal-policy answers whether a principal can do an action, though the full call needs `--policy-source-arn` and `--action-names`, so the sheet stops at the subcommand. get-policy reads the metadata behind a policy ARN, list-policies `--scope` Local hides the AWS-managed noise, and get-role plus list-role-policies show what a role carries.

> **The honest caveat:** CloudTrail records management events by default, and S3 object reads need data events, which cost extra.

> **The lesson:** the account already knows what happened, so ask it in the right order.

## In one line

> **Ask the account what happened.** Four areas, five calls, one trail.

**Who am i**

```bash
aws sts get-caller-identity
```
