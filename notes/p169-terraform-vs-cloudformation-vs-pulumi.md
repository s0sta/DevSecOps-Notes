---
id: p169
title: "Terraform vs CloudFormation vs Pulumi"
slug: terraform-vs-cloudformation-vs-pulumi
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [IaC, Terraform, CloudFormation, Pulumi, DevOps]
source: "LinkedIn post P169 · IT series"
linkedin_date: 2027-10-26
design: matrix
---

# Terraform vs CloudFormation vs Pulumi

Infrastructure as code means defining your servers and networks in files instead of clicking a console. Three popular tools do it in different styles.

## Quick reference

| | **Terraform** | **CloudFormation** | **Pulumi** |
|:--|:--|:--|:--|
| Language | HCL | YAML / JSON | Python, TS, Go |
| Clouds | ✅ Many | ❌ AWS only | ✅ Many |
| State | You manage it | ✅ AWS manages it | You manage it |
| Learning curve | 🟡 Medium | 🟡 Medium | 🟡 Know a language |
| Maturity | ✅ Very mature | ✅ Very mature | 🟡 Newer |
| Best fit | Multi-cloud default | All-in on AWS | Devs who want code |

**How to pick**

- **Terraform** → the multi-cloud default, huge community.
- **CloudFormation** → all-in on AWS, no state to manage.
- **Pulumi** → teams who want real code, not a DSL.

## Explained

Terraform, by HashiCorp, is the de facto standard. You write in HCL, a purpose-built configuration language, and it works across many clouds and services through providers. You manage the state file yourself, usually in a remote backend with locking. Its huge community means there is a module or example for almost anything. It is the usual default, especially for multi-cloud.

CloudFormation is AWS's native tool. You write YAML or JSON, and AWS runs and tracks it for you, so there is no state file to manage and no locking to set up. The trade-off is that it is AWS-only, and the templates get verbose. If you are all-in on AWS, the tight integration and managed state are real advantages.

Pulumi takes a different path: you define infrastructure in a real programming language, Python, TypeScript, Go or others. That means loops, functions, tests and your editor's tooling, which developers love. It is newer and the community is smaller, and you manage state as with Terraform.

### How to choose

Multi-cloud, or want the biggest community: Terraform.  
Entirely on AWS and value managed state: CloudFormation.  
A team that would rather write code than a DSL: Pulumi.

They all achieve the same goal: infrastructure that is version-controlled, reviewable and repeatable. The biggest win is adopting any of them, not which one.

## In one line

> **Same idea, different language.** They all make infrastructure repeatable. Pick for your cloud and team.

**Whatever you pick:** plan and review before every apply
