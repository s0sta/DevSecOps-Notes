---
id: p126
title: "9 AWS CLI commands every admin should know"
slug: 9-aws-cli-commands-every-admin-should-know
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, CloudComputing, DevOps, SysAdmin, Automation]
source: "LinkedIn post P126 · Linux + IT series"
linkedin_date: 2027-07-18
design: steps
---

# 9 AWS CLI commands every admin should know

The AWS console is fine for exploring. For daily work and anything repeatable, the CLI is faster and scriptable. Nine commands worth knowing.

## Quick reference

### Who and where — Know which account you are in

```bash
# Which account and user you are. Run it first, always.
aws sts get-caller-identity
# Separate profiles for each account or environment.
aws configure --profile prod
# Switch profile for this shell session.
export AWS_PROFILE=prod
```

### Storage — Work with S3

```bash
# List objects, like ls for a bucket.
aws s3 ls s3://my-bucket/
# Upload only changes. --delete removes extras.
aws s3 sync ./site s3://my-bucket --delete
# Copy a single file, for example a backup.
aws s3 cp db.sql.gz s3://backups/
```

### Servers and logs — EC2 and CloudWatch

```bash
# Every instance in the region, readable.
aws ec2 describe-instances --output table
# Stop a server. Its EBS disks stay.
aws ec2 stop-instances --instance-ids i-0abc
# Follow CloudWatch logs live, like tail -f.
aws logs tail /aws/lambda/api --follow
```

## Explained

### Who and where

`aws sts get-caller-identity` shows which account and which user or role you are using right now. Run it before anything that changes resources. Most CLI accidents happen in the wrong account.  
`aws configure --profile prod` stores credentials and a default region under a named profile. One profile per account or environment.  
`export AWS_PROFILE=prod` switches profile for the current shell session, so you do not need `--profile` on every command.

### Storage

`aws s3 ls s3://my-bucket/` lists objects in a bucket, like ls for a folder.  
`aws s3 sync ./site s3://my-bucket --delete` uploads only new and changed files. `--delete` removes files from the bucket that no longer exist locally, so run it with `--dryrun` first.  
`aws s3 cp db.sql.gz s3://backups/` copies a single file. A simple way to get backups off the server, ideally into a bucket with versioning turned on.

### Servers and logs

`aws ec2 describe-instances --output table` lists every instance in the current region in a readable table. Add `--query` to pick only the columns you need.  
`aws ec2 stop-instances --instance-ids i-0abc` stops an instance. The EBS volumes stay, so it can be started again. Terminate is permanent.  
`aws logs tail /aws/lambda/api --follow` follows CloudWatch logs live, like `tail -f`, without opening the console.

The habit that matters most: check which account you are in before you press Enter. The CLI is fast, and that includes mistakes.

## In one line

> **Check the account before you press Enter.** The CLI is fast. That includes mistakes.

**Always first**

```bash
aws sts get-caller-identity
```
