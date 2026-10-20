---
id: p221
title: "3 Kubernetes security questions"
slug: 3-kubernetes-security-questions
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, CKS, CyberSecurity, DevSecOps, CloudNative]
source: "LinkedIn post P221 · Cloud / DevSecOps series"
linkedin_date: 2028-02-24
design: quiz
---

# 3 Kubernetes security questions

The final post of this 50-part series, and a fitting place to end: the security layer the whole path has been climbing toward, from Linux fundamentals to the CKS. Three questions. Answer before the reveal.

## Quick reference

**Q1. By default, which pods can a new pod talk to in a cluster?**

- a) Only pods in its namespace
- b) All pods in the cluster
- c) None until RBAC allows it

> **Answer:** b) All pods in the cluster. Without a NetworkPolicy, Kubernetes allows all pod-to-pod traffic. Add a default-deny policy, then allow only what each app needs.

**Q2. What proves a container image really came from your pipeline, unchanged?**

- a) A scan with Trivy
- b) A signature with cosign
- c) A read-only root filesystem

> **Answer:** b) A signature with cosign. Signing with cosign gives provable origin. Scanning finds known CVEs but says nothing about who built the image or whether it was tampered with.

**Q3. Which setting stops a container escape from landing as root on the node?**

- a) runAsNonRoot: true
- b) a resource limit
- c) an Ingress rule

> **Answer:** a) runAsNonRoot: true. runAsNonRoot: true makes the pod refuse to start as root, so an escape gets an unprivileged user instead of control of the host.

## Explained

Question one: by default, which pods can a new pod talk to? The answer is all pods in the cluster. This surprises people: Kubernetes networking is allow-all out of the box. Until you add a NetworkPolicy, any pod can reach any other pod, across every namespace. The fix is a default-deny policy, then explicit allows for the traffic each app actually needs.

Question two: what proves an image really came from your pipeline, unchanged? Signing it with cosign. A scan with Trivy is valuable, but it only finds known vulnerabilities; it says nothing about origin or tampering. A signature answers "did this come from us, unmodified?", which is the heart of supply-chain security.

Question three: what stops a container escape from landing as root on the node? Setting runAsNonRoot: true in the securityContext. The pod then refuses to start as root, so even an escape gets an unprivileged user instead of control of the host. Resource limits and Ingress rules solve different problems.

If you got these, you are thinking the way the CKS wants: assume the defaults are open, and close them deliberately.

That is the series. Fifty posts, from mounting a filesystem to hardening a cluster, plus ten Python scripts you can run today. Thank you for following along.

## In one line

> **Security is the last mile.** From RHCSA to CKS, this is where the path has been heading.

**Keep going:** pick one weak default and fix it this week
