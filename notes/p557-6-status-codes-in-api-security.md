---
id: p557
title: "6 status codes in API security"
slug: 6-status-codes-in-api-security
sections: [devsecops]
topic: "Application & API security"
tags: [API, HTTP, Security, DevSecOps, AppSec]
source: "LinkedIn post P557 · PythonSec series"
linkedin_date: 2030-04-18
design: numbers
---

# 6 status codes in API security

An API returns a status code and thinks the job is done. The code is also a disclosure decision, and the wrong one tells an attacker which objects exist.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **401** | Unauthenticated | Missing or bad credentials. Name the scheme, not the user. | auth |
| **403** | Forbidden | Authenticated but not allowed. The missing role is usually safe to name. | authz |
| **404** | Not found | Use it for another tenant's object. Do not confirm the id. | enum |
| **405** | Method not allowed | Send Allow: GET, POST. It describes the route, not the code. | method |
| **429** | Too many requests | Send Retry-After. Never echo the API key or the account id. | throttle |
| **500** | Server error | Return the request id, never the stack trace or the SQL. | logging |

## Explained

### The six codes

401 means no valid credentials. It should name the scheme in WWW-Authenticate and should not say whether the user exists. A 401 body that lists valid usernames is an enumeration oracle.

403 means the caller is authenticated and still not allowed. Naming the missing role is usually safe; naming the object id confirms it exists.

404 means not found. For another tenant's object, 404 is safer than 403 because a missing id and a forbidden one get the same answer.

405 means the method is wrong for this path. Send Allow: GET, POST, which describes the route contract and not the internals. A 405 still confirms the path exists.

429 means slow down. Send Retry-After and the rate-limit headers, and never echo the API key or the account id. A 429 without Retry-After invites a client to hammer the endpoint.

500 means the server failed. Return the request id and log it; never return the stack trace, the SQL or the upstream hostname.

### The trade-off

> **The honest caveat:** hiding existence behind 404 costs support time and can confuse legitimate clients. Decide per object, and write the decision down.

> **The lesson:** choose the status code for the caller you trust.

## In one line

> **The code is a contract, not a hint.** Every status is a decision about what the caller may know.

**Read the allow header**

```bash
curl -si -X OPTIONS $URL
```
