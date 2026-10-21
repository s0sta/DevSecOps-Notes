---
id: p738
title: "Exposure hunting commands"
slug: exposure-hunting-commands
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, AttackSurface, CommandLine, CloudSecurity, DevSecOps]
source: "LinkedIn post P738 · ASM series"
linkedin_date: 2031-06-15
design: cheatsheet
---

# Exposure hunting commands

Four blocks of commands answer the four questions an exposure review asks: what answers, what listens, what lists, what leaked.

## Quick reference

### HTTP

```bash
curl -sI https://app.example.com/admin
httpx -u app.example.com -title -sc
nuclei -u app.example.com -tags admin
whatweb -a 3 https://app.example.com
curl -s https://example.com/robots.txt
```

### Ports

```bash
nmap -Pn -p 22,3306,6379 203.0.113.10
nmap -sV -p 22,3306,6379 203.0.113.10
naabu -host 203.0.113.10 -top-ports 1000
nc -zv 203.0.113.10 22
masscan -p22,3306 203.0.113.10 --rate 1000
```

### Storage

```bash
aws s3api get-bucket-acl --bucket acme
aws s3 ls s3://acme --no-sign-request
aws s3api get-bucket-policy --bucket acme
gsutil iam get gs://acme-backups
az storage container show-permission -n c1
```

### JavaScript

```bash
rg -n 'AKIA[0-9A-Z]{16}' dist/
rg -n 'sk_live_' dist/*.js
gitleaks detect --no-git -s dist/
semgrep --config p/secrets dist/
trufflehog filesystem dist/
```

## Explained

### HTTP

`curl -sI https://app.example.com/admin` returns the status of a panel. httpx -u app.example.com -title -sc adds the title and status, and nuclei -u app.example.com -tags admin runs the templates. whatweb -a 3 https://app.example.com names the stack, and `curl -s https://example.com/robots.txt` finds the path a site admits. First pass, not a verdict.

### Ports

`nmap -Pn -p 22,3306,6379 203.0.113.10` names the admin and database ports. `nmap -sV` adds the service, naabu -host 203.0.113.10 -top-ports 1000 is the fast sweep, `nc -zv` proves one port answers, and masscan -p22,3306 203.0.113.10 `--rate 1000` covers a range. Run it from outside.

### Storage

`aws s3api get-bucket-acl --bucket acme` shows the grants, and `aws s3 ls s3://acme --no-sign-request` proves anonymous listing. `aws s3api get-bucket-policy --bucket acme` shows the policy; gsutil iam get gs://acme-backups and `az storage container show-permission -n c1` cover the other clouds.

### JavaScript

`rg -n 'AKIA[0-9A-Z]{16}' dist/` finds AWS key ids, `rg -n 'sk_live_' dist/*.js` finds Stripe secrets, and `gitleaks detect --no-git -s dist/` runs a wider set. `semgrep --config p/secrets dist/` adds rules, and trufflehog filesystem dist/ verifies what it finds. Mask the value.

### The fix

The output is a queue: one line per exposure, with an owner and a date.

### Prevention

Run the same four blocks weekly and diff the output.

> **The honest caveat:** a filtered port looks closed, not absent, and a 200 can be a login page. The commands find surface; confirmation is manual.

> **The lesson:** exposure hunting is four habits, not forty tools.

## In one line

> **Ask four questions. Keep four answers.** Four blocks, one loop: run, diff, assign, rescan.

**Ask the first**

```bash
curl -sI https://app.example.com
```
