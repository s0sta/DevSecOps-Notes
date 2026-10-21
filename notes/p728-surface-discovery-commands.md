---
id: p728
title: "Surface discovery commands"
slug: surface-discovery-commands
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, Linux, AWS, CommandLine, AttackSurface]
source: "LinkedIn post P728 · ASM series"
linkedin_date: 2031-05-22
design: cheatsheet
---

# Surface discovery commands

Surface discovery is four command families, and most teams are good at one. The DNS team knows dig, the cloud team knows its CLI, the pentester knows nmap, and nobody owns the certificate log.

## Quick reference

### DNS

```bash
dig +short acme.com A
dig +short acme.com MX
dig +short acme.com NS
dig +trace acme.com
dig +short acme.com TXT
```

### CT

```bash
curl -s 'https://crt.sh/?q=acme.com'
jq -r '.[].name_value' ct.json
jq -r '.[].name_value' ct.json | sort -u
sort -u ct_hosts.txt
grep -v '^\*' ct_hosts.txt
```

### Ports

```bash
nmap -sn 10.0.0.0/24
nmap -sV --top-ports 100 10.0.0.5
nc -zv api.acme.com 443
ss -tulpn | grep LISTEN
masscan -p443 10.0.0.0/24 --rate 1000
```

### Cloud

```bash
aws s3api list-buckets
aws ec2 describe-instances --output table
aws route53 list-hosted-zones
gcloud compute instances list
az vm list -d -o table
```

## Explained

### DNS

`dig +short acme.com A` gives addresses, and the MX and NS queries name the mail and DNS providers. `dig +trace` follows the delegation from the root, which is how you find the zone nobody mentioned. TXT is where SPF, DMARC and verification tokens live, and each token names a service.

### CT

`curl -s 'https://crt.sh/?q=acme.com'` returns the certificate log; add output=json to the query and pipe it to `jq -r '.[].name_value'` for hostnames. `sort -u` collapses the duplicates, and `grep -v '^\*'` removes the wildcards. The result is every name a CA has issued for, including ones that never resolved.

### Ports

`nmap -sn` finds hosts, and `nmap -sV --top-ports 100` names the services on one. `nc -zv` checks a single port in a script. `ss -tulpn` shows what the host listens on, often more than the firewall allows.

### Cloud

`aws s3api list-buckets`, `aws ec2 describe-instances --output table` and `aws route53 list-hosted-zones` are read-only and need only the permissions you already have. `gcloud compute instances list` and `az vm list -d -o table` do the same elsewhere. The cloud inventory is usually complete and usually unread.

> **The honest caveat:** a command that returns nothing is not proof of absence. It is proof that this credential, from this network, saw nothing.

> **The lesson:** four families, one map, and the gap between them is the finding.

## In one line

> **Four families, one map.** The gap between the four answers is the finding.

**Read the log**

```bash
curl -s https://crt.sh/?q=acme.com
```
