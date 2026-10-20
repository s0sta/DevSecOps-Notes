---
id: p284
title: "The shared responsibility model, drawn"
slug: the-shared-responsibility-model-drawn
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [AWS, CloudSecurity, CloudArchitecture, DevOps, CloudNative]
source: "LinkedIn post P284 · Visual series"
linkedin_date: 2028-07-20
design: explainer
---

# The shared responsibility model, drawn

The shared responsibility model fits in one sentence: AWS secures the cloud, you secure what you put in it. The useful version names four layers, because the line is not in the same place for every service.

## Quick reference

### Identity and access

- Users, roles and policies are yours to write
- MFA on the root account, with no exceptions
- Least privilege, reviewed, not guessed
- AWS runs IAM; you decide who gets in

### Data

- Classification, encryption and backups are yours
- AWS encrypts the media; you choose the key
- Bucket and database policies decide access
- Deletion protection is a setting you own

### Platform and configuration

- AWS patches the hypervisor and managed runtime
- On EC2, you patch the guest operating system
- On Lambda and RDS, AWS patches the OS
- Security groups and open ports are your call

### Physical infrastructure

- Buildings, power and cooling belong to AWS
- Hardware and the network fabric are theirs
- Media disposal is their problem, not yours
- You still choose the region your data sits in

> **Note:** The line moves with the service: on EC2 you patch, on Lambda AWS does.

## Explained

**Identity and access**  
Users, roles and policies are yours to write, and so is MFA on the root account. AWS runs IAM, but it has no idea who should be an administrator in your organisation. Least privilege is a decision you make and review, not a checkbox the provider ticks for you.

**Data**  
Classification, encryption and backups are your responsibility. AWS encrypts the physical media; you choose the key, its rotation and who can use it. Bucket and database policies decide who reads the data, and deletion protection is a setting only you can turn on.

**Platform and configuration**  
This layer is genuinely shared. AWS patches the hypervisor and the runtime behind managed services such as Lambda and RDS. On EC2, you patch the guest operating system, and security groups and open ports are your configuration whichever service sits behind them.

**Physical infrastructure**  
Buildings, power, cooling, hardware and the network fabric belong to AWS. Media disposal is their problem, not yours. You still choose the region, and that choice is often the most consequential control you have.

> **The honest caveat:** the line moves with the service, and audits fail where a team assumed the provider had covered a shared control such as patching or configuration management.

> **The lesson:** write down which layer you own before you argue about who forgot it.

## In one line

> **The line moves with the service.** Every managed service redraws it, so read it again.

**Read the model:** aws.amazon.com/compliance
