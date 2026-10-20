---
id: p309
title: "Secrets management: Vault vs cloud KMS vs SOPS"
slug: secrets-management-vault-vs-cloud-kms-vs-sops
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [SecretsManagement, Vault, KMS, SOPS, DevSecOps]
source: "LinkedIn post P309 · Visual series"
linkedin_date: 2028-09-17
design: matrix
---

# Secrets management: Vault vs cloud KMS vs SOPS

A service needs a database password. Three teams answer with three tools, and the argument is usually about taste rather than trust boundaries.

## Quick reference

| | **Vault** | **Cloud KMS** | **SOPS** |
|:--|:--|:--|:--|
| What it stores | Any secret or key | Keys, not secrets | Encrypted files |
| Encryption | Barrier, AES-256-GCM | HSM-backed CMK | Age, PGP or KMS |
| Access model | Token and policy | IAM policy | Key holder only |
| Audit | Audit devices | CloudTrail | Git diffs |
| Rotation | Leases and rotation | Annual or manual | Re-encrypt files |
| Best for | Dynamic secrets | Cloud-native keys | GitOps secrets |

**How to pick**

- **Vault** → dynamic secrets, leases, run it yourself.
- **KMS** → keys stay in the HSM; you keep the envelope.
- **SOPS** → encrypted files in git, decrypted at deploy.

## Explained

### What each one is

Vault stores secrets and hands them out with a lease. A cloud KMS stores keys and never gives the key material back; you call it to encrypt or decrypt. SOPS encrypts a file so the ciphertext can live in git.

### The six rows

Storage: Vault holds any secret or key, KMS holds keys, SOPS holds encrypted files.  
Encryption: Vault uses an AES-256-GCM barrier, KMS uses an HSM-backed key, SOPS uses age, PGP or a cloud KMS.  
Access: Vault checks a token and policy, KMS checks IAM, SOPS trusts the key holder.  
Audit: Vault writes to audit devices, KMS to CloudTrail, SOPS to the git diff.  
Rotation: Vault has leases and rotation, KMS rotates yearly or manually, SOPS re-encrypts.  
Fit: Vault for dynamic secrets, KMS for cloud keys, SOPS for GitOps.

### How to choose

Start from where the secret is used. If it is a database credential that should expire, you want leases. If it is a key that must never leave a boundary, you want KMS. If it is a config file that must ship with the app, SOPS is enough.

> **The honest caveat:** SOPS moves the problem to the key holder. If the age key sits next to the repository, the encryption is decoration.

> **The lesson:** pick the trust boundary first, then the tool that fits it.

## In one line

> **The key is the boundary.** Three tools, three different trust boundaries.

**Check the key**

```bash
aws kms describe-key --key-id $ID
```
