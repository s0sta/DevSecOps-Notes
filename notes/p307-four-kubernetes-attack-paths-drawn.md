---
id: p307
title: "Four Kubernetes attack paths, drawn"
slug: four-kubernetes-attack-paths-drawn
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, CyberSecurity, CloudNative, CKS, DevSecOps]
source: "LinkedIn post P307 · Visual series"
linkedin_date: 2028-09-12
design: explainer
---

# Four Kubernetes attack paths, drawn

A namespace boundary, a network policy and a non-root user feel like enough. Then one pod is compromised, and four well-known paths decide how far the attacker gets. The cluster looks contained until you draw the arrows.

## Quick reference

### Stolen token

- A token copied from a pod or a repo
- The API server sees a real identity
- Bound tokens expire; legacy ones do not
- No exploit needed, just the token

### Privileged pod

- securityContext.privileged: true
- Host devices and every capability
- Container escape gets much easier
- One manifest flag, root on the node

### hostPath mount

- A hostPath of / mounts the node root
- Write a static pod manifest
- The kubelet runs it as root
- A volume, not an exploit

### Cloud metadata

- Pods reach 169.254.169.254
- IMDSv1 needs no token at all
- The node IAM role is the prize
- IMDSv2 asks for a PUT first

## Explained

### Stolen token

Every pod mounts a service account token by default. A bound token expires, but a legacy token does not, and a token copied from a repo or a log is a working identity. The API server cannot tell it from the real pod.

### Privileged pod

A pod with securityContext.privileged: true gets host devices and every capability. Escape to the node is a recipe away, and one manifest flag is all it takes. A privileged pod is a node shell with extra steps.

hostPath mount

A hostPath of / mounts the node root inside the container. From there you can write a static pod manifest, and the kubelet runs it as root. That is not an exploit, it is a volume.

### Cloud metadata

From the pod, 169.254.169.254 answers. IMDSv1 returns credentials with no token, and IMDSv2 asks for a PUT first. Either way, the node's IAM role is the prize, and it is usually wider than the pod's own service account.

> **The honest caveat:** EKS blocks pod access to IMDS on current AMIs, but self-managed nodes and other clouds often do not.

> **The lesson:** every path ends at the node's identity or the node's filesystem.

## In one line

> **The pod is not the boundary.** Four paths, one destination: the node.

**Check a pod**

```bash
kubectl get pod api -o yaml
```
