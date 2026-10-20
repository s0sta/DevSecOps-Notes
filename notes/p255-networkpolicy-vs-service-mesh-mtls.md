---
id: p255
title: "NetworkPolicy vs service mesh mTLS"
slug: networkpolicy-vs-service-mesh-mtls
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Kubernetes, NetworkPolicy, MTLS, DevSecOps, CloudNative]
source: "LinkedIn post P255 · Platform series"
linkedin_date: 2028-05-14
design: compare
---

# NetworkPolicy vs service mesh mTLS

A NetworkPolicy and a service mesh both promise to secure service-to-service traffic, so teams pick one and assume the other is covered. They answer different questions: who may connect, and who is calling.

## Quick reference

| | **NETPOL** | **mTLS** |
|:--|:--|:--|
| Layer | L3/L4 packet rules | L4 identity, L7 policy |
| Identity | Namespace and pod labels | SPIFFE / service account |
| Blocks | Unlisted pod traffic | Calls without a valid cert |
| Encryption | None | mTLS on every hop |
| Ops cost | Low, built into the API | High: proxies and certs |
| Best for | Default-deny east-west | Encrypted service calls |

**NETPOL** (L3/L4 rules, pod to pod): Allows or blocks traffic by pod, namespace, port and protocol.

```bash
kubectl apply -f netpol.yaml
```

**mTLS** (Identity per workload): Both sides prove identity and encrypt every request.

Example: `linkerd viz edges deployment`

- NetworkPolicy → who may connect.
- mTLS → who is actually calling.

## Explained

### The layer

NetworkPolicy is a Kubernetes object enforced by the CNI at layer 3 and 4. It selects pods by label and allows traffic by namespace, pod selector, port and protocol. Once selected, the policy drops what it does not allow. Identity is a label: allowed means trusted.

The mesh adds identity at layer 4 and policy at layer 7. Each workload gets a cryptographic identity tied to its ServiceAccount, and both sides present certificates before a request. Traffic is encrypted and the caller is authenticated.

### What each blocks

NetworkPolicy blocks unlisted traffic. It does not encrypt, and cannot tell two callers on one port apart. In strict mode, mTLS blocks calls without a valid certificate, proving the caller, not the intent.

### The cost

NetworkPolicy is one object, enforced where the CNI runs. mTLS brings a control plane, certificate rotation and a proxy or eBPF agent on every node. That is real weight.

### Where each fits

Default-deny segmentation is NetworkPolicy work. Encryption and workload identity are mesh work. Mature platforms run both, and the mesh still needs authorisation rules.

> **The honest caveat:** a NetworkPolicy is only as strong as its CNI. Some plugins accept the object and ignore it, so test a connection that should fail, not a YAML review.

> **The lesson:** NetworkPolicy decides who may talk; mTLS proves who is talking.

Who may connect, who is calling.
