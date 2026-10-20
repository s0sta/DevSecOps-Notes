---
id: p213
title: "9 commands for Kubernetes security (CKS)"
slug: 9-commands-for-kubernetes-security-cks
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, CKS, CyberSecurity, DevSecOps, CloudNative]
source: "LinkedIn post P213 · Cloud / DevSecOps series"
linkedin_date: 2028-02-06
design: steps
---

# 9 commands for Kubernetes security (CKS)

The CKS is the security end of my Kubernetes path, and it is practical: scan images, harden the cluster against a benchmark, and watch what runs. Nine commands and tools that cover the core, all free and in the CKS curriculum.

## Quick reference

### Scan images — Find vulnerabilities before they ship

```bash
# Scan an image for known CVEs, by severity.
trivy image api:1.4.2
# Scan source and dependencies in a repo.
trivy fs .
# Scan Dockerfiles and manifests for misconfig.
trivy config .
```

### Harden the cluster — Check against the benchmark

```bash
# Check nodes against the CIS Kubernetes benchmark.
kube-bench run
# What can this account actually do? Audit RBAC.
kubectl auth can-i --list
# Pod Security Admission levels per namespace.
kubectl get psa -A
```

### Watch & enforce — Runtime and policy

```bash
# Alert on suspicious runtime behaviour live.
falco
# See which pods are actually isolated.
kubectl get networkpolicy -A
# Enforce a strict pod baseline (PSA: pod-security.kubernetes.io/enforce).
kubectl label ns prod enforce=restricted
```

## Explained

### Scan images

`trivy image api:1.4.2` scans a container image for known vulnerabilities, grouped by severity, and tells you which version fixes each one. Run it in CI and fail the build on criticals.  
`trivy fs .` scans a repo's source and dependencies.  
`trivy config .` scans Dockerfiles and Kubernetes manifests for misconfigurations, like running as root or a missing resource limit.

### Harden the cluster

`kube-bench run` checks your nodes against the CIS Kubernetes benchmark, the official hardening list, and tells you exactly what to fix.  
`kubectl auth can-i --list` shows what an account can really do. RBAC that is too broad is a classic finding; this is how you audit it.  
kubectl get psa, or the namespace labels, shows the Pod Security Admission level: privileged, baseline or restricted.

### Watch and enforce

`falco` watches system calls at runtime and alerts on suspicious behaviour, like a shell spawning in a container or a write to a sensitive path.  
`kubectl get networkpolicy -A` shows which pods are actually isolated. Remember, without a policy, all pod traffic is allowed.  
Labelling a namespace with `pod-security.kubernetes.io/enforce=restricted` enforces a strict baseline: no privileged pods, no host access.

The CKS mindset: shift left with scanning, lock down with benchmarks and RBAC, and keep watch at runtime with Falco.

## In one line

> **Scan, harden, then watch.** CKS is build-time scanning plus run-time defence.

**Start here**

```bash
trivy image <your-image>
```
