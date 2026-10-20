---
id: p219
title: "6 Kubernetes security terms"
slug: 6-kubernetes-security-terms
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, CKS, CyberSecurity, CloudNative, DevSecOps]
source: "LinkedIn post P219 · Cloud / DevSecOps series"
linkedin_date: 2028-02-20
design: reveal
---

# 6 Kubernetes security terms

Kubernetes security has a vocabulary problem: the concepts are not hard, but the names hide them. Learn these six terms and most CKS material suddenly reads clearly. Plain definitions, no jargon.

## Quick reference

- **securityContext** — The block on a pod or container that sets who it runs as and what it can do: user, capabilities, read-only filesystem.
- **Pod Security Admission** — The built-in gate that enforces a baseline per namespace: privileged, baseline or restricted.
- **RBAC** — Role-Based Access Control: who (subjects) can do what (verbs) to which resources. Least privilege lives here.
- **NetworkPolicy** — A firewall for pods, choosing which pods may talk to which. Default is allow-all until you add one.
- **Admission Controller** — Code that inspects every API request and can mutate or reject it before it is stored. Where OPA and signatures enforce.
- **CIS Benchmark** — The industry checklist for hardening a cluster. kube-bench scores your nodes against it.

## Explained

securityContext is the block on a pod or container that decides who it runs as and what it is allowed to do: the user and group ID, whether it can run as root, which Linux capabilities it keeps, and whether its root filesystem is read-only. Most pod hardening is a few lines here.

Pod Security Admission is the built-in gate that enforces a security baseline per namespace. It has three levels: privileged (no restrictions), baseline (sensible minimum) and restricted (locked down). You set it with namespace labels.

RBAC, Role-Based Access Control, defines who can do what to which resources. A Role lists verbs and resources; a binding attaches it to a user or service account. Least privilege is implemented here, and over-broad RBAC is the most common finding.

NetworkPolicy is a firewall for pods, choosing which pods may communicate. Crucially, the default is allow-all: until you add a policy, everything can talk to everything.

Admission Controller is code that inspects every request to the API server and can change or reject it before it is saved. This is where image-signature checks and OPA policies actually enforce.

CIS Benchmark is the industry checklist for hardening a cluster, and kube-bench scores your nodes against it automatically.

## In one line

> **Know the words, own the cluster.** Security is mostly vocabulary you have not met yet.

**See yours**

```bash
kubectl get psa,networkpolicy,roles -A
```
