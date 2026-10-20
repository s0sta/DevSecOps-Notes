---
id: p288
title: "The Azure CLI cheat sheet"
slug: the-azure-cli-cheat-sheet
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [Azure, CloudComputing, DevOps, CommandLine, CloudNative]
source: "LinkedIn post P288 · Visual series"
linkedin_date: 2028-07-30
design: cheatsheet
---

# The Azure CLI cheat sheet

The Azure CLI has one advantage over the portal: every click you make can become a command in a pipeline.

## Quick reference

### Auth

```bash
az login
az account show
az account list --output table
az account set --subscription prod
az ad signed-in-user show
```

### Resources

```bash
az group list
az group create -n rg -l uksouth
az group delete -n rg --no-wait
az resource list -g rg -o table
az deployment group list -g rg
```

### Compute

```bash
az vm list -o table
az vm show -n web -g rg
az vm start -n web -g rg
az vm stop -n web -g rg
az vm list-ip-addresses -g rg -n web
```

### Storage

```bash
az storage account list
az storage account show -n st -g rg
az storage account create -n st -g rg
az storage account keys list -n st -g rg
az storage account check-name -n st
```

## Explained

**Auth**  
`az login` opens the session, `az account show` tells you which subscription you are actually in, and `az account set --subscription prod` switches it. `az account list --output table` shows the choices, and `az ad signed-in-user show` confirms the identity behind the token.

**Resources**  
`az group list` finds the resource groups, and `az group create -n rg -l uksouth` makes one in a named region. `az resource list -g rg -o table` is the inventory, `az deployment group list -g rg` shows what was deployed into a group, and `az group delete -n rg --no-wait` starts the cleanup.

**Compute**  
`az vm list -o table` is the fleet, `az vm show -n web -g rg` is one machine, and start and stop are the two commands you will type most. `az vm list-ip-addresses -g rg -n web` finds the address without opening the portal.

**Storage**  
`az storage account list` is the inventory. Show and create work on one account, keys list fetches the two access keys, and check-name tells you whether a name is free before you create anything.

> **The honest caveat:** the CLI is only as honest as the subscription you selected. Run `az account show` before a destructive command, and never assume the portal and the terminal point at the same tenant.

> **The lesson:** the portal teaches you the shape, and the CLI lets you repeat it.

## In one line

> **Select the account before the command.** The wrong subscription makes every command wrong.

**Who am i**

```bash
az account show
```
