---
id: p246
title: "Terraform vs Crossplane vs Pulumi"
slug: terraform-vs-crossplane-vs-pulumi
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, Crossplane, Pulumi, PlatformEngineering, DevOps]
source: "LinkedIn post P246 · Platform series"
linkedin_date: 2028-04-23
design: matrix
---

# Terraform vs Crossplane vs Pulumi

Terraform, Crossplane and Pulumi all turn infrastructure into code, and the argument between them is usually about taste. The useful question is where the control plane lives and who owns the API.

## Quick reference

| | **Terraform** | **Crossplane** | **Pulumi** |
|:--|:--|:--|:--|
| Model | HCL and state | Kubernetes CRDs | General-purpose code |
| Control plane | CLI plus state | Runs in the cluster | CLI plus backend |
| Drift | 🟡 plan shows it | ✅ reconciles it | 🟡 preview shows it |
| Day-2 ops | 🟡 apply and import | ✅ kubectl and GitOps | 🟡 code and pipelines |
| Learning curve | 🟡 HCL plus state | ❌ Kubernetes plus YAML | ✅ a language you know |
| Best for | ✅ broad cloud estates | ✅ platform APIs | ✅ app teams |

**How to pick**

- **Terraform** → provision anything, anywhere, from one state.
- **Crossplane** → expose platform APIs as Kubernetes objects.
- **Pulumi** → let app teams use the language they already know.

## Explained

### Three models

Terraform describes infrastructure in HCL and keeps a state file that maps resources to the real world. The CLI is the control plane: plan, apply, import.  
Crossplane runs controllers inside a Kubernetes cluster. Its resources are CRDs, and its control plane is the cluster itself, reconciling continuously.  
Pulumi uses a general-purpose language such as TypeScript, Python, Go or .NET and a state backend. The CLI or an operator runs the program.

### Where they differ

Drift. Terraform plan shows it when you run it; Crossplane reconciles it without being asked; Pulumi preview and refresh show it.  
Day-2 operations. Terraform is apply and import; Crossplane is kubectl and GitOps; Pulumi is code and pipelines.  
Learning curve. HCL plus state is its own language; Crossplane adds Kubernetes and composition, the steepest; Pulumi is fastest if you already write code.

### How to choose

Terraform for a broad estate across clouds and SaaS. Crossplane when you want to offer platform APIs as Kubernetes objects. Pulumi when application teams own their infrastructure in a language they already use.

> **The honest caveat:** each has a sharp edge. Terraform has remote state to secure and lock; Crossplane adds a control plane to operate; Pulumi needs a language runtime and a state backend.

> **The lesson:** pick by the interface you want to support, not by the syntax you like.

## In one line

> **Model the API, not the YAML.** The tool matters less than who owns the interface.

**Prove the diff**

```bash
terraform plan
```
