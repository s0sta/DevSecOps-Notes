---
id: p137
title: "Terraform vs Ansible"
slug: terraform-vs-ansible
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, Ansible, DevOps, IaC, CloudComputing]
source: "LinkedIn post P137 · IT series"
linkedin_date: 2027-08-12
design: compare
---

# Terraform vs Ansible

Terraform and Ansible are both "infrastructure as code", and teams argue about which to use. The honest answer is that they do different jobs and work well together.

## Quick reference

| | **TERRAFORM** | **ANSIBLE** |
|:--|:--|:--|
| Main job | Build infrastructure | Configure servers |
| Model | Declarative, keeps state | Mostly procedural |
| State file | Yes, tracks reality | No state |
| Language | HCL | YAML playbooks |
| Agent | Agentless (APIs) | Agentless (SSH) |
| Best at | Cloud resources | OS and app setup |

**TERRAFORM** (Provisioning): Creates and tracks infrastructure: servers, networks, databases.

```bash
terraform apply
```

**ANSIBLE** (Configuration): Configures what is already there: packages, files, services.

```bash
ansible-playbook site.yml
```

- Terraform → create the servers and networks.
- Ansible → set up what runs on them. Often used together.

## Explained

Terraform provisions infrastructure. You describe the servers, networks, load balancers and databases you want, and terraform apply makes the cloud match that description. Its superpower is state: Terraform keeps a file that records what it created, so it knows the difference between what you asked for and what exists, and changes only what is needed. Destroy an environment and recreate it identically with one command.

Ansible configures machines. Once a server exists, an Ansible playbook installs packages, writes config files, starts services and deploys your app. It connects over SSH, needs no agent on the target, and reads as a readable list of steps in YAML.

### The clearest way to see the split

Terraform answers "what infrastructure should exist?" It is declarative and tracks state.  
Ansible answers "what should be true on this machine?" It is mostly procedural, running tasks in order, and keeps no state file.

Where they overlap: Terraform can run some configuration, and Ansible can create cloud resources. But each is clumsy at the other's job. Terraform managing files on a server, or Ansible tracking hundreds of cloud resources without state, both get painful.

The common pattern: Terraform builds the servers and networks, then hands off to Ansible to configure them. Many teams run exactly this.

Build with Terraform. Configure with Ansible.
