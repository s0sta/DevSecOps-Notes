---
id: p183
title: "9 Azure CLI commands for AZ-104"
slug: 9-azure-cli-commands-for-az-104
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [Azure, AZ104, CloudComputing, DevOps, CLI]
source: "LinkedIn post P183 · Cloud / DevSecOps series"
linkedin_date: 2027-11-28
design: steps
---

# 9 Azure CLI commands for AZ-104

AZ-104 is phase 2 of my plan, and the fastest way to learn Azure is the CLI, not clicking through the portal. Nine az commands cover most of the lab work, and they are repeatable, which the portal is not.

## Quick reference

### Set up — Sign in and scope

```bash
# Sign in. Add --use-device-code on a headless box.
az login
# Pick the subscription you are working in.
az account set --subscription <id>
# A resource group to hold your lab.
az group create -n rg-lab -l westeurope
```

### Build — A tiny environment

```bash
# Create a VM with sensible defaults.
az vm create -g rg-lab -n vm1 --image Ubuntu2404
# A virtual network for your resources.
az network vnet create -g rg-lab -n vnet1
# Storage, with a globally unique name.
az storage account create -g rg-lab -n st$RANDOM
```

### Inspect & clean — See it, then delete it

```bash
# Everything in the group, readable.
az resource list -g rg-lab -o table
# Public and private IPs at a glance.
az vm list-ip-addresses -o table
# Delete the group and stop the billing.
az group delete -n rg-lab --yes
```

## Explained

### Set up

`az login` signs you in through the browser; add `--use-device-code` on a server with no browser.  
`az account set --subscription <id>` picks the subscription, so you do not accidentally build in the wrong one. az account show confirms where you are.  
`az group create -n rg-lab -l westeurope` makes a resource group, a container that lets you delete everything at once later.

### Build

`az vm create -g rg-lab -n vm1 --image Ubuntu2404` spins up a VM with sensible defaults and returns its public IP.  
az network vnet create makes a virtual network, the backbone your resources sit in.  
az storage account create needs a globally unique name, which is why `$RANDOM` is handy in a lab.

### Inspect and clean

`az resource list -g rg-lab -o table` shows everything in the group in a readable table. -o table is the flag that makes the CLI pleasant.  
`az vm list-ip-addresses -o table` gives you IPs without hunting through the portal.  
`az group delete -n rg-lab --yes` removes the whole group, which is the single most important habit on a free account: it stops the billing.

> **The rule that saves money:** build in a resource group, and delete the group when the lab is done. A forgotten VM is the classic surprise on the Azure bill.

## In one line

> **Delete the lab when you finish.** A forgotten VM is the most common surprise on the bill.

**Always after a lab**

```bash
az group delete -n rg-lab --yes --no-wait
```
