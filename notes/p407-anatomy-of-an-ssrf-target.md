---
id: p407
title: "Anatomy of an SSRF target"
slug: anatomy-of-an-ssrf-target
sections: [devsecops]
topic: "Application & API security"
tags: [SSRF, AppSec, CloudSecurity, CyberSecurity, DevSecOps]
source: "LinkedIn post P407 · DevSecOps series"
linkedin_date: 2029-05-03
design: anatomy
---

# Anatomy of an SSRF target

An SSRF report rarely starts with a payload. It starts with a feature: fetch this image, import this URL, check this webhook. The server fetches, and it can reach places your browser cannot.

## Quick reference

```text
http://169.254.169.254/latest/meta-data/iam/
```

| Part | Name | What it means |
|:--|:--|:--|
| `http://` | Scheme | Plain HTTP: the metadata endpoint is not TLS. |
| `169.254.169.254` | Link-local IP | The instance metadata service, reachable from the host network. |
| `/latest` | API version | The versioned root; latest is an alias that can change. |
| `/meta-data` | Metadata path | Instance identity, user data and the IAM branch live here. |
| `/iam/` | Credential path | Lists the roles; one role returns temporary access keys. |

## Explained

### The string

The target is http://169.254.169.254/latest/meta-data/iam/. Read it in five parts. http:// is the scheme: plain HTTP, not HTTPS. 169.254.169.254 is a link-local address, and on AWS it is the metadata service.

### The path

`/latest` selects the API version. `/meta-data` is the metadata root, where instance identity and user data live. `/iam/` is the credential branch: list the roles, then read a role to receive temporary access keys.

### Why it works

The attacker needs no shell access, only one parameter the server will fetch. A shortener, a redirect, a DNS name for the link-local range, or a webhook tester can point it inward. The response returns through that same feature.

### The fix

Block link-local and private ranges at the egress layer, allow-list the hosts a fetch feature may call, and do not follow redirects into a different range. On AWS, require IMDSv2, which needs a PUT to get a session token, and set the hop limit to 1 so a container cannot reach the host metadata.

> **The honest caveat:** IMDSv2 raises the bar rather than closing the hole. A proxy that allows PUT, or an SSRF with method control, can still mint the token; the egress allow-list is the control that lasts.

> **The lesson:** any URL the server fetches is a request you did not write.

## In one line

> **The cloud trusts its own network.** A server that fetches URLs can fetch its own credentials.

**Test the block**

```bash
curl -m 2 http://169.254.169.254
```
