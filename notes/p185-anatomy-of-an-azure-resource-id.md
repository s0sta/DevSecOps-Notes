---
id: p185
title: "Anatomy of an Azure resource ID"
slug: anatomy-of-an-azure-resource-id
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [Azure, AZ104, CloudComputing, IAM, DevOps]
source: "LinkedIn post P185 · Cloud / DevSecOps series"
linkedin_date: 2027-12-02
design: anatomy
---

# Anatomy of an Azure resource ID

Everything in Azure has a resource ID: one long path that uniquely identifies it. Once you can read it, the CLI, role assignments and policies all make more sense, because they all point at this path. It reads left to right, from broadest to most specific.

## Quick reference

```text
/subscriptions/8f3a../resourceGroups/rg-prod/providers/Microsoft.Compute/virtualMachines/vm-web-01
```

| Part | Name | What it means |
|:--|:--|:--|
| `/subscriptions/8f3a..` | Subscription | Which subscription pays for and owns it. |
| `/resourceGroups/rg-prod` | Resource group | The container that holds related resources. |
| `/providers/Microsoft.Compute` | Provider | The Azure service namespace, here compute. |
| `/virtualMachines` | Type | The kind of resource within that provider. |
| `/vm-web-01` | Name | The resource's own name. The part you chose. |

## Explained

`/subscriptions/8f3a..`. is the subscription. The top-level billing and ownership boundary. Every resource lives inside exactly one, and the GUID is how automation targets the right one.

`/resourceGroups/rg-prod` is the resource group. A container for related resources that share a lifecycle, so you can deploy, manage and delete them together. Good naming here keeps an account readable.

`/providers/Microsoft.Compute` is the resource provider, the Azure service namespace. Compute for VMs, Storage for storage accounts, Network for networking. This is Azure's catalogue of services.

`/virtualMachines` is the resource type within that provider. A provider offers many types; this one is VMs.

`/vm-web-01` is the resource name, the part you chose when you created it.

### Why it matters in practice

Role-based access control and Azure Policy are applied at a scope, and the scope is one of these path segments. Grant a role at the subscription and it covers everything; grant it at a resource group and it covers just that group; grant it at a single resource ID and it covers only that one. Reading the ID tells you exactly how broad a permission really is.

## In one line

> **One ID names everything.** Every CLI call, role and policy points at this path.

**See an id**

```bash
az resource list -o tsv --query '[].id'
```
