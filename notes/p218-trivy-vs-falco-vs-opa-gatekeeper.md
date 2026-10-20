---
id: p218
title: "Trivy vs Falco vs OPA Gatekeeper"
slug: trivy-vs-falco-vs-opa-gatekeeper
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, CKS, DevSecOps, CloudNative, CyberSecurity]
source: "LinkedIn post P218 · Cloud / DevSecOps series"
linkedin_date: 2028-02-17
design: matrix
---

# Trivy vs Falco vs OPA Gatekeeper

Three open-source tools cover most Kubernetes security, and they are easy to confuse because all three are about safety. The clearest way to tell them apart is the question each one answers and the moment it acts. All three are in the CKS.

## Quick reference

| | **Trivy** | **Falco** | **OPA/Gatekeeper** |
|:--|:--|:--|:--|
| Question | What CVEs are here? | What is happening now? | Is this allowed? |
| When | Build time | Runtime | Admission |
| Watches | Images & files | System calls | API requests |
| Catches | Known vulns | Live attacks | Bad config |
| Acts by | Failing CI | Alerting | Rejecting |
| CKS domain | Supply chain | Runtime | Hardening |

**How to pick**

- **Trivy** → scan images and code before they ship.
- **Falco** → detect suspicious behaviour while pods run.
- **OPA/Gatekeeper** → block non-compliant resources at the door.

## Explained

Trivy asks: what vulnerabilities are in here? It scans container images, filesystems and config for known CVEs and misconfigurations, at build time. It acts by failing CI so a vulnerable image never reaches the registry. This is the supply-chain and shift-left tool.

Falco asks: what is happening right now? It watches system calls at runtime and alerts on suspicious behaviour, a shell opening inside a container, an unexpected write to a sensitive path, a connection to a strange IP. It acts by alerting, so you see an attack in progress. This is the runtime-detection tool.

OPA Gatekeeper asks: is this allowed? It evaluates every request to the Kubernetes API against your policies at admission time and rejects anything non-compliant, a privileged pod, an image from an untrusted registry, a missing label. It acts by blocking the resource at the door. This is the policy-enforcement tool.

### How they fit together

They are not competitors; they cover different moments. Trivy scans before, Falco watches during, Gatekeeper enforces at the gate. A hardened cluster runs all three: scan images in CI, enforce policy on admission, detect anomalies at runtime.

## In one line

> **Three tools, three moments.** Scan before, watch during, enforce at the gate.

**Layer them:** Trivy in CI, Gatekeeper on admission, Falco at runtime
