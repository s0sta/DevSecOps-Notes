---
id: p375
title: "The secure code review cheat sheet"
slug: the-secure-code-review-cheat-sheet
sections: [devsecops]
topic: "Application & API security"
tags: [DevSecOps, AppSec, CodeReview, CyberSecurity, SecureCoding]
source: "LinkedIn post P375 · DevSecOps series"
linkedin_date: 2029-02-18
design: cheatsheet
---

# The secure code review cheat sheet

The code review is the last place a cheap fix is still possible, and the diff is where everyone looks. The flaw is usually one line outside it, in the call path nobody opened.

## Quick reference

### Input

```bash
grep -rn 'eval(' --include=*.py .
grep -rn 'shell=True' --include=*.py .
grep -rn 'innerHTML' --include=*.js .
grep -rn 'pickle.loads' .
grep -rn 'execute(f' .
```

### Auth

```bash
grep -rn 'verify=False' .
grep -rn 'jwt.decode' .
grep -rn 'algorithm=none' .
grep -rn '== password' .
grep -rn 'is_admin = True' .
```

### Secrets

```bash
grep -rnE '(api_key|secret)=' .
grep -rn 'BEGIN RSA PRIVATE KEY' .
gitleaks detect --no-git -v
trufflehog filesystem . --only-verified
git log -p -S 'password' | head
```

### Crypto

```bash
grep -rnE 'md5|sha1' .
grep -rn 'MODE_ECB' .
grep -rn 'random.random' .
grep -rn 'AES.new(' .
openssl x509 -in cert.pem -text -noout
```

## Explained

**Input**  
Input first. eval, pickle.loads and shell=True turn data into code; innerHTML turns a string into markup; execute(f marks an f-string query. Grep for each, then read the path from the request to the call.

**Auth**  
Auth next. verify=False disables certificate checks, a jwt.decode call that trusts the token's algorithm is where the none algorithm gets in, a password comparison with == leaks timing, and a hard-coded is_admin is a privilege bug with a friendly name.

**Secrets**  
Secrets. The regex finds assignments, gitleaks and trufflehog find the history, and `git log -p -S` finds a password removed from the file but not from the commit. Rotate first, rewrite history second.

**Crypto**  
Crypto last. md5 and sha1 are broken for passwords, MODE_ECB leaks patterns, random.random is not a key, and a certificate you never inspect is a trust decision you did not make. openssl x509 prints the dates and the key size.

> **The honest caveat:** grep finds spellings, not logic. A clean run means the obvious mistakes are absent, not that the code is safe.

> **The lesson:** a review is a reading exercise, and a grep is only the index.

## In one line

> **Read the code, not the diff.** The dangerous line is usually the caller, not the change.

**Grep the diff**

```bash
git diff -U0 | grep '^+'
```
