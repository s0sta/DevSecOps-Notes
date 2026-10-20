---
id: p193
title: "Anatomy of a Terraform resource block"
slug: anatomy-of-a-terraform-resource-block
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, IaC, DevOps, CloudComputing, Azure]
source: "LinkedIn post P193 · Cloud / DevSecOps series"
linkedin_date: 2027-12-21
design: anatomy
---

# Anatomy of a Terraform resource block

Every Terraform configuration is built from resource blocks, and once you can read the first line of one, the rest of HCL falls into place. A block has four parts.

## Quick reference

```text
resource "azurerm_linux_vm" "web" { ... }
```

| Part | Name | What it means |
|:--|:--|:--|
| `resource` | Block type | Declares something Terraform will create and manage. |
| `"azurerm_linux_vm"` | Resource type | Provider name + what to make. Sets the arguments allowed. |
| `"web"` | Local name | Your label in code: azurerm_linux_vm.web.id. Not the cloud name. |
| `{ ... }` | The body | Arguments inside: name, size, location, tags. |

## Explained

resource is the block type. It tells Terraform this is something to create and manage in the real world, as opposed to a data source (which only reads) or a variable. It is the most common block you will write.

"azurerm_linux_virtual_machine" is the resource type. The first part names the provider (azurerm for Azure, aws for AWS), and the rest names what to build. The type decides which arguments are valid inside the body, which is why the docs are organised by resource type.

"web" is the local name, your label for this resource within the configuration. It is how you reference the resource elsewhere, like azurerm_linux_virtual_machine.web.id. Important: this is not the name of the resource in the cloud. The cloud name is an argument inside the body. People mix these up constantly.

{ ... } is the body, where the arguments live: the actual name, size, location, network and tags. This is the configuration itself.

### Why the type-and-name pair matters

Together, the type and local name form a unique address inside your configuration, and that address is how everything connects. A subnet references its virtual network by address; an output exports a resource's attribute by address. State tracks resources by this address too, which is why renaming one can make Terraform want to destroy and recreate it.

## In one line

> **Type plus name is the address.** That pair is how every other resource refers to this one.

**See the plan**

```bash
terraform plan -out=tfplan
```
