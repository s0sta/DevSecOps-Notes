---
id: p253
title: "IRSA vs GKE Workload Identity vs Azure Workload Identity"
slug: irsa-vs-gke-workload-identity-vs-azure-workload-identity
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, AWS, Azure, GCP, DevSecOps]
source: "LinkedIn post P253 · Platform series"
linkedin_date: 2028-05-09
design: matrix
---

# IRSA vs GKE Workload Identity vs Azure Workload Identity

IRSA, GKE Workload Identity and Azure Workload Identity solve one problem: a pod needs a cloud credential, and a static key is not acceptable. All three exchange a Kubernetes service account token for short-lived credentials.

## Quick reference

| | **IRSA** | **GKE WI** | **Azure WI** |
|:--|:--|:--|:--|
| Mechanism | OIDC token to STS | OIDC token to IAM | OIDC token to Entra |
| Trust anchor | EKS OIDC provider | GKE workload pool | AKS OIDC issuer |
| Scope | Per service account | KSA to GSA | Per federated cred |
| Setup | 🟡 Role, trust, annotate | 🟡 Binding, annotate | 🟡 Credential, annotate |
| Portability | ❌ AWS only | ❌ GCP only | ❌ Azure only |
| Best for | ✅ EKS clusters | ✅ GKE clusters | ✅ AKS clusters |

**How to pick**

- **IRSA** → the EKS way: a KSA annotated with an IAM role.
- **GKE** → map a KSA to a Google service account.
- **Azure** → federate a KSA with a managed identity.

## Explained

### Mechanism and trust

Each pod gets a projected token for its Kubernetes service account. The cloud STS validates it against the cluster's OIDC issuer and returns temporary credentials. No secret is stored in the pod.  
The trust anchor is what differs. IRSA trusts the EKS cluster's OIDC provider. GKE trusts the workload identity pool of the project. Azure trusts the AKS cluster's OIDC issuer through a federated identity credential.

### Scope and setup

IRSA maps one Kubernetes service account to one IAM role. GKE maps a KSA to a Google service account with an IAM binding. Azure maps a KSA to a managed identity through a federated credential.  
Setup has the same shape everywhere: enable the cluster issuer, create the cloud identity, annotate the Kubernetes service account.

### Portability and fit

None of them ports. The annotation key, trust policy and token audience are provider-specific, so moving cloud means rebuilding the identity layer.  
Each is native to its cluster: IRSA on EKS, Workload Identity on GKE, federated identity on AKS. Use the managed option, not a custom token broker.

> **The honest caveat:** the trust policy is the security boundary. A wildcard subject or audience lets any service account in the cluster assume the role.

> **The lesson:** the mechanism is portable; the trust anchor is not.

## In one line

> **One identity, three clouds.** The mechanism is the same; the trust anchor is not.

**Check the issuer**

```bash
aws eks describe-cluster --name prod
```
