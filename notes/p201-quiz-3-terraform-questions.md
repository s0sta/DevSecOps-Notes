---
id: p201
title: "Quiz: 3 Terraform questions"
slug: quiz-3-terraform-questions
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, IaC, DevOps, CloudComputing, InterviewPrep]
source: "LinkedIn post P201 · Cloud / DevSecOps series"
linkedin_date: 2028-01-09
design: quiz
---

# Quiz: 3 Terraform questions

Terraform Associate is phase 3 of my plan. Three questions that test whether you really understand how Terraform thinks, not just the commands. Try each before the answer.

## Quick reference

**Q1. What does the Terraform state file actually store?**

- a) Your HCL code
- b) A map of your config to real resources
- c) Your cloud credentials

> **Answer:** b) A map of your config to real resources. State maps each resource in your config to the real object, so Terraform knows what exists and what to change.

**Q2. You run terraform apply with no saved plan. What happens?**

- a) It applies instantly
- b) It shows a plan and asks you to confirm
- c) It only validates

> **Answer:** b) It shows a plan and asks you to confirm. apply re-plans and prompts for yes. Applying a saved plan file skips the prompt and runs exactly what you reviewed.

**Q3. Which command previews changes without making them?**

- a) terraform plan
- b) terraform refresh
- c) terraform show

> **Answer:** a) terraform plan. plan shows what would be created, changed or destroyed. Always read it, especially anything marked destroy.

## Explained

1. What does the Terraform state file actually store?

> **Answer:** a map from your configuration to the real resources. State records which real-world object (by ID) corresponds to each resource in your code, plus their current attributes. This is how Terraform knows the difference between what you asked for and what already exists, so it can change only what is needed. It is not your HCL (that is your code), and it should never contain plaintext credentials you put there, though it can capture sensitive attributes, which is why state must be stored securely and remotely.

2. You run terraform apply with no saved plan. What happens?

> **Answer:** it creates a plan, shows it, and asks you to confirm with yes. Many people think apply runs immediately. It does not, unless you pass -auto-approve or give it a saved plan file. Applying a saved plan (terraform apply tfplan) skips the prompt and runs exactly what you already reviewed, which is the safest pattern in automation.

3. **Which command previews changes without making them?**

> **Answer:** terraform plan. It shows everything that would be created, changed or destroyed, and changes nothing. Reading it, especially any line marked destroy, is the single most important habit in Terraform. refresh updates state from reality; show displays existing state.

The core of Terraform is two ideas: state (what exists) and plan (what will change). Most mistakes come from misunderstanding one of them.

## In one line

> **State and plan. That is the core.** Most Terraform mistakes come from misunderstanding those two.

**The safe loop**

```bash
terraform plan -out=tfplan && terraform apply tfplan
```
