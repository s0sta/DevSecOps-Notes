---
id: p216
title: "5 Kubernetes security mistakes"
slug: 5-kubernetes-security-mistakes
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, CKS, CyberSecurity, DevSecOps, CloudNative]
source: "LinkedIn post P216 · Cloud / DevSecOps series"
linkedin_date: 2028-02-13
design: dontdo
---

# 5 Kubernetes security mistakes

Kubernetes ships with convenient defaults, not safe ones. Most CKS findings, and most real incidents, come down to the same five. Here is each mistake and the one-line fix.

## Quick reference

**1. Don't**

containers running as root

A container escape becomes root on the node.

**Do instead**

```bash
runAsNonRoot: true
```

The pod refuses to start as root. Escapes get a nobody user.

**2.** ❌ **no NetworkPolicy** — Every pod can talk to every other pod, cluster-wide.  
✅ **a default-deny NetworkPolicy** — Deny all, then allow only the traffic each app needs.

**3.** ❌ **wide-open RBAC (cluster-admin)** — One leaked token owns the whole cluster.  
✅ **least-privilege Roles** — Grant only the verbs and resources an account truly uses.

**4.** ❌ **secrets as plain env vars** — They leak into logs, crashes and kubectl describe.  
✅ **mounted Secrets, encrypted at rest** — Enable etcd encryption; mount as files, not env.

**5.** ❌ **no resource limits** — One pod can starve a node. A DoS from inside.  
✅ **requests and limits on every pod** — Cap CPU and memory so one workload can't take the node down.

## Explained

### Running as root

By default a container can run as root, so a container escape lands as root on the node. Set `runAsNonRoot: true` in the pod's securityContext and the pod refuses to start as root. An escape then gets an unprivileged user instead of the keys to the host.

### No NetworkPolicy

Without a NetworkPolicy, every pod can reach every other pod across the whole cluster. One compromised pod can scan and attack everything. Apply a default-deny policy, then allow only the specific traffic each app needs.

### Wide-open RBAC

Handing out cluster-admin "to make it work" means one leaked token owns the cluster. Grant least-privilege Roles: only the verbs and resources an account actually uses. Audit with kubectl auth can-i.

### Secrets as plain env vars

Secrets passed as environment variables leak into logs, crash dumps and kubectl describe. Mount them as files instead, and enable encryption at rest for etcd so they are not stored in plaintext.

### No resource limits

A pod with no limits can consume a whole node's CPU and memory, a denial of service from inside. Set requests and limits on every pod so one workload cannot take a node down.

None of these are exotic. They are defaults left unchanged. Securing them is most of what hardening a cluster means.

## In one line

> **Secure the defaults.** Kubernetes ships open for convenience. Production is your job.

**Audit now:** kubectl get pods -A -o jsonpath on securityContext
