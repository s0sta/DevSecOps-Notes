---
id: p257
title: "How a pod becomes cluster admin"
slug: how-a-pod-becomes-cluster-admin
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, RBAC, CloudSecurity, DevSecOps, CKS]
source: "LinkedIn post P257 · Platform series"
linkedin_date: 2028-05-18
design: pipeline
---

# How a pod becomes cluster admin

A pod does not need a vulnerability to become cluster admin. It needs a ServiceAccount token, a permissive RoleBinding and a namespace that still allows privileged pods. Here is the path.

## Quick reference

1. **A token is stolen** — A compromised pod reads its mounted ServiceAccount token. · *token*
2. **List secrets** — It reads Secrets in its namespace, including credentials. · *secrets*
3. **Find a privileged SA** — A RoleBinding shows which ServiceAccount can create pods. · *rbac*
4. **Create a pod as that SA** — The API server runs the new pod with the stronger identity. · *pod create*
5. **Mount the node** — hostPath / exposes the node filesystem and kubelet creds. · *hostPath*
6. **Take the cloud role** — Node instance profile gives the pod cloud rights. · *cloud*

## Explained

### The path

1. **A token is stolen.** Every pod mounts a projected token at `/var/run/secrets/kubernetes.io/serviceaccount/token` unless automount is disabled. A compromised container reads it first.

2. **List secrets.** If the ServiceAccount can list Secrets in its namespace, credentials come back in plaintext: database passwords, API keys, sometimes a cloud key. It is the most common RBAC over-grant.

3. **Find a privileged SA.** RoleBindings show which accounts can create pods. The CI account often can, and its Role may also allow Secrets or pods/exec. `kubectl auth can-i --list --as=system:serviceaccount:shop:api` answers it.

4. **Create a pod as that SA.** Anyone who can create a pod can usually set serviceAccountName in the spec. The API server admits it; the kubelet mounts the stronger token.

5. **Mount the node.** With hostPath: /, the container reads the node's filesystem, often including the kubelet kubeconfig.

6. **Take the cloud role.** The metadata endpoint at 169.254.169.254 may return the node's instance profile credentials. The cluster admin is now the cloud account.

### Where it stops

> **The honest caveat:** Pod Security Admission at baseline or restricted rejects hostPath and privileged pods, so this chain needs a namespace that allows them. Inventory it first.

> **The lesson:** the token is not the breach; the binding behind it is.

## In one line

> **One pod is the whole cluster.** A stolen token is a foothold; weak RBAC makes it the account.

**Prove the path**

```bash
kubectl auth can-i create pods
```
