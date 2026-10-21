---
id: p739
title: "Four exposures that persist"
slug: four-exposures-that-persist
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, AttackSurface, AppSec, CloudSecurity, RiskManagement]
source: "LinkedIn post P739 · ASM series"
linkedin_date: 2031-06-17
design: explainer
---

# Four exposures that persist

Every remediation sprint closes the same tickets and leaves the same four exposures. Each one sits outside a different team's patch window.

## Quick reference

### Admin panel

- 200 at /admin, no SSO, no owner in the CMDB
- Survives because nobody probes it from outside
- Fix: SSO or VPN, then remove the old DNS record
- A 200 is reachability, not a login bypass

### Leaked key

- AWS, Google, Stripe or bearer, shipped in a bundle
- Still valid because rotation breaks a build
- Fix: revoke, rotate, then purge the CDN cache
- Deleting the line leaves the key in every cache

### Public bucket

- Public ACL, private policy, account block off
- ListBucket returns keys, sizes and dates
- Fix: block public access, then remove the grant
- Test with an unauthenticated request, not the console

### Legacy API

- Deprecated in the spec, still routed by the gateway
- No security scheme, no owner, no removal date
- Fix: remove the route, not just the documentation
- Every gateway route is an API, documented or not

> **Note:** The four that survive a sprint because each has no owner.

## Explained

### Admin panel

The panel answers 200, has no SSO, and is owned by a team that calls it internal. It survives because nobody probes it from outside and the DNS record is old.

### Leaked key

The key is in a bundle, still valid, and shared by three services. It survives because rotation breaks a build and the build has no owner.

### Public bucket

The ACL says public and the policy says private. It survives because the console shows a private badge and nobody tests with an unauthenticated request.

### Legacy API

The route is deprecated, still routed, and documented in a wiki that nobody updates. It survives because removal needs a date, a team and a consumer list.

### The fix

Assign each one an owner and a removal step: SSO, rotation, block plus ACL cleanup, gateway removal. A date without an owner is a wish.

### Prevention

Review the same four every month, with the same four questions. The list should get shorter; if it does not, the process is the exposure.

> **The honest caveat:** these four persist because each is a decision nobody made, not because the fix is hard. The technical work is an afternoon; the ownership is the delay.

> **The lesson:** persistence is an ownership failure, not a technical one.

## In one line

> **Four doors, four owners.** Admin panel, leaked key, public bucket, legacy API: four owners, not four tools.

**Find the owner**

```bash
grep -c owner findings.csv
```
