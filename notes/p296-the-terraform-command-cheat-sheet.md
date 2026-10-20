---
id: p296
title: "The Terraform command cheat sheet"
slug: the-terraform-command-cheat-sheet
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, IaC, DevOps, CloudComputing, CICD]
source: "LinkedIn post P296 · Visual series"
linkedin_date: 2028-08-17
design: cheatsheet
---

# The Terraform command cheat sheet

The plan says three to add, none to change and one to destroy, and everyone scrolls to the bottom. Terraform is four verbs and twenty commands, and the state file decides whether you sleep.

## Quick reference

### Init

```bash
terraform init
terraform init -upgrade
terraform init -reconfigure
terraform providers
terraform version
```

### Plan

```bash
terraform plan -out=tfplan
terraform plan -var-file=prod.tfvars
terraform show -no-color tfplan
terraform validate
terraform fmt -check -recursive
```

### State

```bash
terraform state list
terraform state show aws_instance.api
terraform state pull
terraform state mv module.old module.new
terraform apply -refresh-only
```

### Import

```bash
terraform import aws_s3_bucket.logs logs
terraform plan -generate-config-out=gen.tf
terraform state list | grep logs
terraform plan -target=aws_s3_bucket.logs
terraform state rm aws_s3_bucket.logs
```

## Explained

### Init

Init prepares the directory: downloads providers, writes the lock file. -upgrade moves to the newest allowed versions, -reconfigure forgets a moved backend. `terraform providers` lists what is installed, and `terraform version` names the binary.

### Plan

Plan shows what would change. -out=tfplan records the decision for the apply, -var-file picks production values. show -no-color prints it for a pull request, validate catches type errors, and fmt -check -recursive fails CI on unformatted files.

### State

State maps configuration to real resources. state list names the addresses, state show reads one, state pull prints the file. state mv moves an address without touching the cloud, and apply -refresh-only updates state from reality without changing infrastructure.

### Import

Import adopts what already exists. `terraform import aws_s3_bucket.logs logs` writes it into state, plan -generate-config-out=`gen.tf` writes matching HCL, state list | grep logs confirms it, and state rm drops it from state without deleting the bucket.

> **The honest caveat:** -target is for recovery, not routine work. A targeted plan ignores everything outside the target, so a green run says little about the whole configuration.

> **The lesson:** the plan is the review and the state is the database. Treat both with the care that implies.

## In one line

> **Plan first. Then apply.** The plan is the review; the state is the database.

**Review the plan**

```bash
terraform show -no-color tfplan
```
