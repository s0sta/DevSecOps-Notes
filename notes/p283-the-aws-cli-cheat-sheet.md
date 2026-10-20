---
id: p283
title: "The AWS CLI cheat sheet"
slug: the-aws-cli-cheat-sheet
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, CloudComputing, DevOps, CommandLine, CloudNative]
source: "LinkedIn post P283 · Visual series"
linkedin_date: 2028-07-18
design: cheatsheet
---

# The AWS CLI cheat sheet

The console is fine until the same question arrives for the tenth account, or you need the answer inside a pipeline. The AWS CLI is the same API with a shorter path.

## Quick reference

### Identity

```bash
aws sts get-caller-identity
aws iam list-users
aws iam list-roles
aws iam get-role --role-name app
aws configure list
```

### Compute

```bash
aws ec2 describe-instances
aws ec2 describe-instance-status
aws lambda list-functions
aws lambda invoke --function-name fn out
aws ecs list-clusters
```

### Storage

```bash
aws s3 ls
aws s3 cp file.txt s3://bucket/
aws s3 sync ./dist s3://bucket/
aws s3 presign s3://bucket/key
aws s3api get-bucket-policy --bucket b
```

### Network

```bash
aws ec2 describe-vpcs
aws ec2 describe-subnets
aws ec2 describe-route-tables
aws ec2 describe-security-groups
aws elbv2 describe-load-balancers
```

## Explained

**Identity**  
`aws sts get-caller-identity` is the first command in any account: it tells you who you are and which account you are in. `aws iam list-users` and `aws iam list-roles` show what exists, `aws iam get-role --role-name app` shows one role, and `aws configure list` shows the profile, key and region the CLI is actually using.

**Compute**  
`aws ec2 describe-instances` lists the fleet, and `aws ec2 describe-instance-status` adds the health checks. `aws lambda list-functions` and aws lambda invoke are enough for most function work, and `aws ecs list-clusters` finds the container clusters.

**Storage**  
`aws s3 ls` is still the fastest bucket inventory. aws s3 cp and aws s3 sync move data, aws s3 presign makes a temporary URL without changing the object, and aws s3api get-bucket-policy shows the policy that can open the bucket to the world.

**Network**  
`aws ec2 describe-vpcs`, describe-subnets, describe-route-tables and describe-security-groups read the four parts of a VPC, and `aws elbv2 describe-load-balancers` shows what sits in front of the app.

> **The honest caveat:** the CLI silently takes the profile and region from your shell. A command that works on your laptop can hit the wrong account in CI, so run `aws sts get-caller-identity` first, every time.

> **The lesson:** the console is a view, and the CLI is the same view that you can put in a script.

## In one line

> **Type it once, then script it.** Twenty commands beat a browser tab and a memory.

**Who am i**

```bash
aws sts get-caller-identity
```
