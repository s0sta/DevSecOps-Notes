---
id: p256
title: "5 Kubernetes RBAC mistakes"
slug: 5-kubernetes-rbac-mistakes
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, RBAC, CloudSecurity, DevSecOps, CKS]
source: "LinkedIn post P256 · Platform series"
linkedin_date: 2028-05-16
design: dontdo
---

# 5 Kubernetes RBAC mistakes

RBAC is the easiest control to grant and the hardest one to take back. These five turn a stolen token into a cluster-wide incident.

## Quick reference

**1.** ❌ **cluster-admin for CI** — The pipeline can delete any namespace, secret or CRD it can reach.  
✅ **A namespaced Role per app** — CI writes to one namespace and cannot see the rest.

**2.** ❌ **Wildcard verbs and resources** — '\*' on '\*' is cluster-admin with extra steps, and nobody reviews it.  
✅ **Only the verbs the job calls** — get, list and watch on the three resources it actually uses.

**3.** ❌ **Default ServiceAccount token** — Every pod mounts a token the API server accepts, needed or not.  
✅ **Disable token automount** — Set automountServiceAccountToken: false unless the pod calls the API.

**4.** ❌ **One binding for all namespaces** — A ClusterRoleBinding grants the same rights in kube-system too.  
✅ **RoleBinding per namespace** — A RoleBinding scopes the same Role to one namespace at a time.

**5.** ❌ **Bindings nobody removes** — A contractor's access outlives the contract; the token still works.  
✅ **Review bindings quarterly** — `kubectl auth can-i --list` shows what each account still holds.

## Explained

### The grants

1. **cluster-admin for CI.** The pipeline that deploys everything is often bound to cluster-admin, because it made the first deploy work. It can delete any namespace, read any Secret and change any CRD. Give it a namespaced Role per app instead.

2. **Wildcard verbs and resources.** verbs: ["\*"] on resources: ["\*"] is cluster-admin with extra steps, and nobody reviews what it includes. The grant grows with every new resource, without a commit. List the verbs the job calls.

### The leftovers

3. **Default ServiceAccount tokens.** Every pod mounts a token unless you turn it off, and the API server accepts it. Anything that can read the pod's filesystem can act as that ServiceAccount. Set automountServiceAccountToken: false unless the pod calls the API.

4. **One binding for all namespaces.** A ClusterRoleBinding grants the same rights everywhere, including kube-system. A RoleBinding keeps the same Role inside one namespace, which is usually the intent.

5. **Bindings nobody removes.** Access has no expiry. A contractor's RoleBinding outlives the contract, and the token still works a year later. Review bindings quarterly and delete what no account uses.

> **The honest caveat:** RBAC only guards the API server. A pod that can mount hostPath / or run privileged reaches the node credentials, and no Role stops that.

> **The lesson:** every binding is a door. Grant the smallest one, then check who still has a key.

## In one line

> **Every binding is a door left open.** RBAC is additive: nothing expires on its own.

**Audit the defaults**

```bash
kubectl get clusterrolebindings -o wide
```
