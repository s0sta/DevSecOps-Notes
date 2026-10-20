---
id: p220
title: "The CKS exam by the numbers"
slug: the-cks-exam-by-the-numbers
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, CKS, CyberSecurity, CloudNative, DevSecOps]
source: "LinkedIn post P220 · Cloud / DevSecOps series"
linkedin_date: 2028-02-22
design: numbers
---

# The CKS exam by the numbers

The Certified Kubernetes Security Specialist is the security capstone of my roadmap, and like the CKA it is entirely hands-on: you fix and harden a real cluster against the clock. Knowing how it is weighted tells you where to spend your study time. Here it is in numbers.

## Quick reference

| Number | What | Why it matters | |
|:--|:--|:--|:--|
| **6** | Domains | The exam is split into six weighted areas. Know the weights. | exam |
| **20%** | Supply chain | Tied for the biggest domain: scanning, signing, SBOMs. | weight |
| **20%** | Microservice vuln | Secrets, mTLS, pod security, container sandboxing. | weight |
| **20%** | Runtime security | Falco, behavioural analytics, immutable containers. | weight |
| **2 hr** | Time limit | Hands-on, in a real cluster. Speed matters. | format |
| **67%** | Pass score | And you must already hold a valid CKA to sit it. | pass |

## Explained

Six domains. The exam is divided into six areas, each with a published weight, and ignoring the weights is the classic mistake. Three of them dominate.

Twenty percent, supply chain security. Tied for the largest domain: minimising base images, scanning with tools like Trivy, signing images, and working with SBOMs. This reflects where the industry is most worried right now.

Twenty percent, microservice vulnerabilities. Managing secrets properly, mutual TLS between services, pod security standards, and container sandboxing with runtimes like gVisor.

Twenty percent, runtime security. Behavioural detection with Falco, immutable containers, and auditing. Catching attacks while they happen.

Those three alone are 60 percent of the exam. The remaining 40 is cluster setup (NetworkPolicies, CIS benchmarks), cluster hardening (RBAC, restricting API access) and system hardening (minimising the host, AppArmor, seccomp).

Two hours, hands-on, in a live cluster. Speed and muscle memory matter as much as knowledge.

Sixty-seven percent to pass, and you must already hold a valid CKA to even sit it. CKS builds on CKA; you cannot skip the operations layer.

## In one line

> **Study the weights.** Three domains are 60 percent of the exam. Start there.

**Practise live:** harden a real cluster, not slides
