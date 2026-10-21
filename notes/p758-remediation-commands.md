---
id: p758
title: "Remediation commands"
slug: remediation-commands
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [VulnerabilityManagement, CommandLine, CyberSecurity, Linux, DevOps]
source: "LinkedIn post P758 · ASM series"
linkedin_date: 2031-07-31
design: cheatsheet
---

# Remediation commands

The fix phase has four command blocks worth knowing: patch a host, prove the fix, record the exception, and escalate on a date.

## Quick reference

### Patch

```bash
apt-get install --only-upgrade nginx
dnf update --security
kubectl rollout restart deploy/api
systemctl restart nginx
pip install -U 'django>=4.2.15'
```

### Verify

```bash
python3 rescan_diff.py b.json a.json
curl -sS https://api-01/healthz
dpkg -l | grep nginx
trivy image --quiet api:2.1
nmap -sV -p 443 api-01
```

### Exception

```bash
python3 exception_register.py reg.json
jq '.exceptions[].expires' reg.json
grep -c '"expires": ""' reg.json
date -d '+90 days' +%F
```

### Escalate

```bash
python3 escalation.py f.json o.json
mail -s "overdue" owner@example.com
grep -c committee escalation.txt
sort -k2 -n overdue.txt | tail -5
```

## Explained

### Patch

The patch block upgrades one package without moving the rest: apt-get with `--only-upgrade`, dnf with `--security`, kubectl rollout restart for a new image, systemctl for a config change, pip with a pinned floor. Run one, then read the version back.

### Verify

The verify block proves the change. rescan_diff compares two exports with the same checks, curl reads the version endpoint, dpkg and trivy name what is installed, and nmap shows what still answers on the port.

### Exception

The exception block keeps an acceptance honest: the register script reports what expired, jq lists the dates, grep counts the blank ones, and date prints the ninety-day limit. An exception without a date is a permanent one.

### Escalate

The escalation block moves a finding to a person: run escalation with the findings and the owner map, mail the result, count the committee tier, sort the overdue list by age.

### Read them in order

The sheet draws four rows, each with a monogram tile, the block name and the commands to the right, in the order a fix travels from the package to the person.

> **The honest caveat:** a command that prints a version is not proof that the vulnerable path is gone.

> **The lesson:** read the command, then the result.

## In one line

> **Read the command, then the result.** A version string proves an install, not a fix.

**Patch one host**

```bash
apt-get install --only-upgrade nginx
```
