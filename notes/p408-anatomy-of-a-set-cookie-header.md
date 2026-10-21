---
id: p408
title: "Anatomy of a Set-Cookie header"
slug: anatomy-of-a-set-cookie-header
sections: [devsecops]
topic: "Application & API security"
tags: [WebSecurity, Cookies, AppSec, CyberSecurity, DevSecOps]
source: "LinkedIn post P408 · DevSecOps series"
linkedin_date: 2029-05-06
design: anatomy
---

# Anatomy of a Set-Cookie header

A session cookie is a bearer token with a browser attached. The Set-Cookie header is where the server sets the rules, and six attributes decide how far the secret travels.

## Quick reference

```text
session=abc; Secure; HttpOnly; SameSite=Lax; Max-Age=3600; Path=/
```

| Part | Name | What it means |
|:--|:--|:--|
| `session=abc` | Name and value | The session ID is the secret: anyone who has it is the user. |
| `Secure` | HTTPS only | The browser sends it only over TLS; plain HTTP never sees it. |
| `HttpOnly` | No JavaScript | document.cookie cannot read it, so an XSS cannot steal it. |
| `SameSite=Lax` | Cross-site rule | Not sent on cross-site POSTs; a top-level GET still carries it. |
| `Max-Age=3600` | Lifetime | One hour in seconds. Expires is the absolute-date alternative. |
| `Path=/` | Scope | Sent to every path on the host. Narrow it where you can. |

## Explained

### The six parts

`session=abc` is the name and value. The value is the session identifier: anyone who has it is the user, so it should be random and long.

Secure means the browser sends the cookie only over HTTPS. Without it, one plain-HTTP request leaks the session to anyone on the path.

HttpOnly hides the cookie from document.cookie, so a script injected into the page cannot read it. It does not stop that script from making requests as the user.

SameSite=Lax stops the browser sending the cookie on cross-site POSTs, while a top-level GET navigation still carries it. Lax is the common default now; Strict is tighter and None requires Secure.

`Max-Age=3600` sets a lifetime of one hour in seconds. Expires does the same with an absolute date, and Max-Age wins when both appear.

Path=/ scopes the cookie to every path on the host. Narrow it to `/app` when the session is only needed there.

### What is missing

Domain is absent, so the cookie is host-only. There is no __Host- prefix and no Partitioned attribute. Those are choices too.

> **The honest caveat:** HttpOnly does not make XSS harmless, SameSite=Lax does not stop CSRF on GET side effects, and Secure protects the wire, not the browser or the server.

> **The lesson:** every attribute removes one way to steal or misuse the cookie.

## In one line

> **The cookie is a policy.** Six attributes decide who can read it and where it travels.

**Audit the header**

```bash
curl -sI https://example.com | grep -i cookie
```
