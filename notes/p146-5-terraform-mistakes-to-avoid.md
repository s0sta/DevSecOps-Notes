---
id: p146
title: "5 Terraform mistakes to avoid"
slug: 5-terraform-mistakes-to-avoid
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, IaC, DevOps, CloudComputing, BestPractices]
source: "LinkedIn post P146 · IT series"
linkedin_date: 2027-09-02
design: dontdo
---

# 5 Terraform mistakes to avoid

Terraform is powerful because it tracks the real state of your infrastructure. That same state is where most team pain comes from. Five mistakes, and the safer habit for each.

## Quick reference

**1.** ❌ **`terraform.tfstate` in git** — It holds secrets and causes conflicts between people.  
✅ **remote state (S3 + lock)** — Shared, encrypted, and locked so two applies cannot clash.

**2.** ❌ **edit resources in the console** — Terraform and reality drift. The next apply fights you.  
✅ **change it in code, then apply** — The code stays the single source of truth.

**3. Don't**

```bash
terraform apply (no plan)
```

You find out what it changes while it changes it.

**Do instead**

terraform plan, read, then apply

See every create, change and destroy first.

**4.** ❌ **hard-coded secrets in .tf** — They end up in state and in git history.  
✅ **variables + a secrets manager** — Inject at apply time; keep secrets out of code.

**5.** ❌ **one giant `main.tf` for everything** — One mistake can destroy prod and dev together.  
✅ **separate state per environment** — Blast radius stays inside one environment.

## Explained

1. Committing `terraform.tfstate` to git
   The state file records everything Terraform manages, including secrets in plain text, and two people committing it causes ugly conflicts. Instead: use remote state in S3, Azure Blob or Terraform Cloud, with state locking so two applies cannot run at once.

2. Editing resources by hand in the console
   Click-changing something Terraform manages creates drift: the code and reality no longer match, and the next apply tries to "fix" your manual change or fails. Instead: make every change in code and apply it. If you must touch the console in an emergency, reconcile the code straight after.

3. Running terraform apply without a plan
   apply will happily destroy and recreate resources. Running it blind means you discover what it does while it is doing it. Instead: `terraform plan -out=tfplan`, read every line, especially anything that says destroy, then apply that exact plan.

4. Hard-coding secrets in .tf files
   Secrets written into Terraform files end up in the state file and in git history forever. Instead: use variables and pull secrets from a manager like Vault, AWS Secrets Manager or environment variables at apply time.

5. One giant configuration for everything
   When dev, staging and prod share one state, a single mistake can damage all of them. Instead: separate state per environment, so the blast radius of any change stays contained.

The thread through all five: state is shared, and plan before apply is not optional.

## In one line

> **State is shared. Treat it with care.** Most Terraform pain is state and plan discipline.

**Always before apply**

```bash
terraform plan -out=tfplan
```
