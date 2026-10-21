---
id: p507
title: "Ingress vs Gateway API"
slug: ingress-vs-gateway-api
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, Ingress, GatewayAPI, Networking, CloudNative]
source: "LinkedIn post P507 · Network series"
linkedin_date: 2029-12-23
design: compare
---

# Ingress vs Gateway API

An ingress is three lines of YAML and a controller you forgot you installed. Gateway API is the same job split across roles, and the migration is not a rename.

## Quick reference

| | **INGRESS** | **GATEWAY** |
|:--|:--|:--|
| API | One object, v1 | Role-based CRDs |
| Protocols | HTTP and HTTPS | HTTP, gRPC, TCP, TLS |
| Routes on | Host and path | Host, path, header, weight |
| Ownership | One team owns it all | Infra and app split |
| Controllers | Traefik, HAProxy, Kong | Envoy Gateway, Cilium |
| Status | Frozen since 1.19 | GA, installed separately |

**INGRESS** (The stable L7 entry point): One object for host and path rules, handled by a controller you install.

```bash
kubectl get ingress
```

**GATEWAY** (The role-oriented successor): A family of CRDs that splits infrastructure from application routing.

```bash
kubectl get gateway,httproute
```

- Ingress → one object, host and path rules.
- Gateway → role-based routes, more protocols.

## Explained

### The API

Ingress is one stable object, `networking.k8s.io/v1` since Kubernetes 1.19, with host and path rules and a reference to an IngressClass. It handles HTTP and HTTPS. Gateway API is a family of CRDs, GatewayClass, Gateway and HTTPRoute among them, and it adds gRPC, TCP, UDP and TLS routes.

### Routes and ownership

Ingress matches host and path. Gateway API matches host, path, header, method and query, and can split traffic by weight between backends. With Ingress, one team usually owns the controller, the certificate and every rule. Gateway API separates the infrastructure owner, who runs the Gateway, from the application owner, who attaches a route. That split is the real feature.

### Controllers and status

Ingress controllers are mature: Traefik, HAProxy, Kong and others. Gateway API implementations are younger but real: Envoy Gateway, Cilium, Istio and others. Ingress is frozen, not deprecated; it will keep working. Gateway API is generally available but still installed as CRDs, so it is not in the core API server.

> **The honest caveat:** Gateway API is more capable and has more moving parts. If one team owns one controller and needs only host and path, Ingress is still the smaller system.

> **The lesson:** choose by ownership model, not by feature count.

Ingress -> one object, host and path rules.  
Gateway -> role-based routes, more protocols.
