---
id: p170
title: "9 ansible commands to start with"
slug: 9-ansible-commands-to-start-with
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Ansible, DevOps, Automation, Linux, SysAdmin]
source: "LinkedIn post P170 · IT series"
linkedin_date: 2027-10-28
design: terminal
---

# 9 ansible commands to start with

Ansible configures many servers at once, over SSH, with no agent to install on them. You can start with one-line commands today and grow into full playbooks later. Nine to begin with.

## Quick reference

### Can I reach the hosts?

```bash
# check SSH and Python on every host
ansible all -m ping
# gather facts: OS, IP, memory, and more
ansible all -m setup
# run one command on a group of hosts
ansible web -a 'uptime'
```

### Make changes

```bash
# install a package. -b runs with sudo
ansible web -b -m apt -a 'name=nginx state=present'
# restart a service everywhere at once
ansible web -b -m service -a 'name=nginx state=restarted'
# push a file to every host
ansible web -b -m copy -a 'src=app.conf dest=/etc/app/'
```

### Repeatable runs

```bash
# dry run: see what would change
ansible-playbook site.yml --check
# run against one host first
ansible-playbook site.yml --limit web01
# keep secrets encrypted at rest
ansible-vault edit secrets.yml
```

## Explained

### Can I reach the hosts?

`ansible all -m ping` is the first test. It confirms Ansible can reach each host over SSH and run Python there. It is not a network ping; it is an end-to-end check.  
`ansible all -m setup` gathers facts about each host: OS, IP addresses, memory, disks. These facts are what playbooks use to make decisions.  
`ansible web -a 'uptime'` runs a single command on every host in the web group. Great for quick checks across a fleet.

### Make changes

`ansible web -b -m apt -a 'name=nginx state=present'` installs a package everywhere. -b means become, running with sudo. Modules like apt are idempotent: run them again and nothing changes if nginx is already there.  
`ansible web -b -m service -a 'name=nginx state=restarted'` restarts a service across the whole group at once.  
`ansible web -b -m copy -a 'src=app.conf dest=/etc/app/'` pushes a file to every host.

### Repeatable runs

`ansible-playbook site.yml --check` is a dry run. It shows what would change without changing anything. Always run this first.  
`ansible-playbook site.yml --limit web01` runs a playbook against one host before the whole fleet.  
`ansible-vault edit secrets.yml` keeps secrets encrypted at rest, so credentials never sit in plain text in your repo.

The path: ad-hoc commands to learn, playbooks to make it repeatable.

## In one line

> **One command, every server.** Start with ad-hoc commands, then grow into playbooks.

**Try it**

```bash
ansible all -m ping
```
