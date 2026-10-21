---
id: p403
title: "The API security testing cheat sheet"
slug: the-api-security-testing-cheat-sheet
sections: [devsecops]
topic: "Application & API security"
tags: [APISecurity, AppSec, CheatSheet, CyberSecurity, DevSecOps]
source: "LinkedIn post P403 · DevSecOps series"
linkedin_date: 2029-04-24
design: cheatsheet
---

# The API security testing cheat sheet

An API test is not a scanner run. You have a token, a second account and a shell, and the goal is to prove what one user can do to another.

## Quick reference

### Auth

```bash
curl -si -u user:pass $API/me
curl -si $API/me -b jar.txt
jwt decode $TOKEN
jwt decode $TOKEN | jq -r .exp
curl -si -X POST $API/login -d @a.json
```

### Authz

```bash
curl -si $API/admin -b bob.txt
curl -si $API/users/2 -b bob.txt
curl -si $API/users/2 -b alice.txt
curl -si -X DELETE $API/u/2 -b bob.txt
```

### Input

```bash
curl -si "$API/q?x=%27"
curl -si "$API/q?x=%3Cscript%3E"
curl -si "$API/f?p=../../etc/passwd"
curl -si $API/q?x=%00
curl -si --path-as-is $API/../admin
```

### Limits

```bash
curl -si $API?page=999999999
curl -si -X POST $API/login -d @big.json
curl -si --max-time 1 $API/slow
seq 100 | xargs -P20 -n1 curl -s $API
```

## Explained

### Auth

Start with authentication. `curl -si -u user:pass $API/me` establishes a baseline: status line and headers, no follow and no noise. Replay the session with -b `jar.txt`, then read the token itself. jwt decode `$TOKEN` shows the header and claims, and piping it to `jq -r .exp` turns the expiry into a number you can compare. A login POST with -d @`a.json` keeps the body out of history.

### Authz

Authorisation needs two identities, and that is the only honest test. Request `$API`/users/2 as bob, then as alice, and compare both responses. If both return 200 with the same record, the object check is missing. Repeat on `$API`/admin and on a DELETE: read, role and write are three different failures.

### Input

Input tests ask whether data becomes syntax. Send a single quote, a script tag, a traversal path, a null byte, and a .. path. `--path-as-is` keeps the request honest.

### Limits

Limits are about cost. Ask for page 999999999, post a large body, hold a slow request, and send a small burst. A 429 or a timeout is a control; a 500 is a finding.

> **The honest caveat:** a 403 on one ID proves nothing about the collection endpoint or the write path, and a WAF block may hide the bug rather than fix it.

> **The lesson:** test with two accounts, or you are only testing one.

## In one line

> **Two identities, one bug.** A second account is the cheapest authorisation test you own.

**Replay as alice**

```bash
curl -si $API/users/2 -b alice.txt
```
