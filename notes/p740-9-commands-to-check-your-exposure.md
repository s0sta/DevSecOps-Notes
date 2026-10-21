---
id: p740
title: "9 commands to check your exposure"
slug: 9-commands-to-check-your-exposure
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, CommandLine, CloudSecurity, AttackSurface, DevSecOps]
source: "LinkedIn post P740 · ASM series"
linkedin_date: 2031-06-19
design: terminal
---

# 9 commands to check your exposure

Nine commands, three passes: probe from outside, confirm what answered, scope how far it reaches.

## Quick reference

### What answers?

```bash
# an admin path answers 200
curl -sI https://app.example.com/admin
# admin and database ports
nmap -Pn -p 22,3306 203.0.113.10
# the panel names itself
curl -s https://example.com/robots.txt
```

### Is it real?

```bash
# 200, not a 302 to /login
curl -sI https://app.example.com/admin/
# a public grant
aws s3api get-bucket-acl --bucket acme
# admin route still declared
jq '.paths|keys' openapi.json
```

### How far?

```bash
# key in the shipped bundle
rg -l 'AKIA[0-9A-Z]{16}' dist/
# anonymous listing works
aws s3 ls s3://acme --no-sign-request
# route added 41 days ago
git log -S 'admin' --oneline -- src/
```

## Explained

### Probe

The first pass asks what is there. `curl -sI` on the admin path, nmap on the admin and database ports, `robots.txt` for the paths the site admits. It is noisy and cheap; do it from outside your network.

### Confirm

The second pass removes the false positives. Does /admin return 200 or redirect to /login? Does the bucket ACL really grant AllUsers? Does the OpenAPI document still declare the admin route? A 403 can be a WAF; a 200 can be a login page.

### Scope

The third pass asks what the exposure touches. rg for a key pattern in the bundle, an anonymous S3 list, git log for when the admin route appeared. Scope decides whether this is a ticket or an incident.

### The fix

Close the port, remove the grant, rotate the key. The nine commands produce evidence, not a fix.

### Prevention

Run the nine weekly and alert on a new 200, a new AllUsers grant or a new key pattern. The loop is the control.

> **The honest caveat:** reachability is cheap to test and impact is expensive to prove. The nine commands tell you where to look, not what an attacker got.

> **The lesson:** a 200 is a door, not a finding.

## In one line

> **A 200 is a door, not a finding.** Reachability is the evidence; the owner is the fix.

**Try it**

```bash
curl -sI https://app.example.com/admin
```
