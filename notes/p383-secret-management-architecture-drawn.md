---
id: p383
title: "Secret management architecture, drawn"
slug: secret-management-architecture-drawn
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [SecretsManagement, DevSecOps, Vault, CloudSecurity, AppSec]
source: "LinkedIn post P383 · DevSecOps series"
linkedin_date: 2029-03-08
design: architecture
---

# Secret management architecture, drawn

A static cloud key in a CI variable is a password with no expiry. Secret management replaces it with three tiers and a credential that dies on time.

## Quick reference

- **Apps:** Application (APP) · CI job (CI)
- **Vault:** Secret store (VAULT) · Dynamic credentials (DYN)
- **Cloud:** KMS (KMS) · Target service (TGT)

**Request flow:** Application → Secret store → Dynamic credentials → Target service; Secret store → KMS; Application → Target service; CI job → Secret store

## Explained

### Apps

The first tier is the caller. The application authenticates to the secret store with its workload identity, not with a root token in a config file. The CI job proves which repository and branch it is through OIDC, and gets a short-lived token back.

### Vault

The second tier is the store and the credentials it mints. The store keeps static values encrypted and audits every read. Dynamic credentials are generated on request: a database user with a TTL, an IAM session, an SSH certificate. When the lease expires the credential stops working, whether or not the job cleaned up.

### Cloud

The third tier is where the secret is used. KMS wraps the root key, so that key never sits in the store's memory. The target service accepts the short-lived credential and enforces its own authorisation. The application still connects to the target, but never owns a long-lived password.

The arrows carry the design. Both callers point at the store, the store points at dynamic credentials and KMS, the credentials point at the target, and the application's arrow carries the borrowed credential.

> **The honest caveat:** a short TTL limits the damage after a leak, but not a compromised workload asking for a credential while its identity is valid. Scope the role, not just the clock.

> **The lesson:** not a bigger vault, but a credential that expires before an attacker uses it.

## In one line

> **Borrow the key, never store it.** A credential that expires is worth more than a vault that grows.

**Check a lease**

```bash
vault read database/creds/app
```
