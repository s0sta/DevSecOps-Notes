---
id: p411
title: "AppSec terms, decoded"
slug: appsec-terms-decoded
sections: [devsecops]
topic: "Application & API security"
tags: [AppSec, CyberSecurity, WebSecurity, DevSecOps, APISecurity]
source: "LinkedIn post P411 · DevSecOps series"
linkedin_date: 2029-05-13
design: reveal
---

# AppSec terms, decoded

Six acronyms carry most of the application security conversation. Each one is a mechanism, not a mood, and knowing the mechanism tells you where to look.

## Quick reference

- **XSS** — Untrusted input runs as script in another user's browser, so it acts with their session.
- **CSRF** — A third-party page makes the browser send a state-changing request the user never intended.
- **SSRF** — The server is tricked into fetching an attacker-chosen URL, including internal addresses.
- **IDOR** — An object ID is accepted without an ownership check, so changing it reads another user's data.
- **CORS** — A browser rule that lets a page read another origin's response only when that origin allows it.
- **CSP** — A response header that tells the browser which scripts, styles, frames and hosts may load.

## Explained

### In the browser

XSS, cross-site scripting, is untrusted input running as script in another user's browser, so it acts with that session. CSRF, cross-site request forgery, is a third-party page making the browser send a state-changing request the user never intended; SameSite cookies and per-request tokens are the defence.

### On the server

SSRF, server-side request forgery, is the server itself fetching an attacker-chosen URL, including internal addresses and cloud metadata. IDOR, insecure direct object reference, is an object ID accepted without an ownership check, so changing it reads or writes another user's data. It is an authorisation failure, not an input bug.

### Policy

CORS, cross-origin resource sharing, is a browser rule that lets a page read another origin's response only when that origin allows it. It is not a server breach by itself; it controls what a malicious site can read with the user's browser. CSP, content security policy, is a response header naming the scripts, styles, frames and hosts a page may load; it mitigates XSS and cannot fix an injection alone.

> **The honest caveat:** the acronyms overlap. IDOR is one kind of broken authorisation, CSRF is often blocked by SameSite, and a loose CORS rule is a finding only when credentials or sensitive data are involved.

> **The lesson:** name the mechanism and the fix follows.

## In one line

> **Learn the word, see the bug.** Six acronyms that explain most API findings.

**Check the header**

```bash
curl -sI $URL | grep -i content-security
```
