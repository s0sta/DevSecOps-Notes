---
id: p149
title: "9 terraform commands every engineer should know"
slug: 9-terraform-commands-every-engineer-should-know
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, IaC, DevOps, CloudComputing, Automation]
source: "LinkedIn post P149 · IT series"
linkedin_date: 2027-09-09
design: steps
---

# 9 terraform commands every engineer should know

Terraform has many commands, but nine cover almost all real work, from setting up a project to getting out of trouble safely.

## Quick reference

### The core loop — Init, plan, apply

```bash
# Download providers and set up the backend. Run it first.
terraform init
# Show every change and save it. Read before applying.
terraform plan -out=tfplan
# Apply exactly what you reviewed. No surprises.
terraform apply tfplan
```

### Stay safe — See and check before you change

```bash
# Format every file to the standard style.
terraform fmt -recursive
# Catch syntax and type errors without touching the cloud.
terraform validate
# Everything Terraform currently manages.
terraform state list
```

### Out of trouble — Targeted and careful

```bash
# Plan one resource when debugging.
terraform plan -target=aws_instance.web
# Bring an existing resource under management.
terraform import aws_s3_bucket.b my-bucket
# Tear it all down. Read the plan twice.
terraform destroy
```

## Explained

### The core loop

`terraform init` downloads the providers and sets up the backend where state is stored. Run it first in any new project, and again after adding a provider or module.  
`terraform plan -out=tfplan` shows exactly what will be created, changed or destroyed, and saves that plan to a file. Reading it is the single most important habit in Terraform.  
`terraform apply tfplan` applies the saved plan, so what runs is exactly what you reviewed. Running apply with no saved plan re-plans and asks for confirmation, which is fine, but applying a saved plan removes any gap between review and action.

### Stay safe

`terraform fmt -recursive` formats every file to the canonical style, so diffs stay clean and reviews focus on real changes.  
`terraform validate` checks syntax and types without contacting the cloud. Fast feedback, ideal in CI.  
`terraform state list` shows everything Terraform currently manages. Your map of reality.

### Out of trouble

`terraform plan -target=aws_instance.web` limits the plan to one resource, useful when debugging a specific change. Use it sparingly, not as a habit.  
terraform import brings an existing, manually created resource under Terraform's management without recreating it.  
`terraform destroy` tears everything down. Powerful and permanent, so read that plan twice, especially the count.

The thread through all of it: plan is the command that matters. apply should never surprise you.

## In one line

> **Plan is the most important command.** Read it every time. apply should never surprise you.

**The safe loop**

```bash
terraform plan -out=tfplan && terraform apply tfplan
```
