---
id: p225
title: "Helm vs Kustomize"
slug: helm-vs-kustomize
sections: [devsecops]
topic: "GitOps & Helm"
tags: [Helm, Kustomize, Kubernetes, GitOps, DevOps]
source: "LinkedIn post P225 · Platform series"
linkedin_date: 2028-03-05
design: compare
---

# Helm vs Kustomize

Helm and Kustomize both stop you copying YAML between environments, and they are often framed as rivals. In practice they solve two different problems, and many teams run both.

## Quick reference

| | **HELM** | **KUSTOMIZE** |
|:--|:--|:--|
| Approach | Templates + values | Patches on plain YAML |
| Packaging | Charts, versions, registries | None built in |
| Learning curve | A day for the basics | An hour for the basics |
| Per environment | `values-prod.yaml` | overlays/prod |
| Readable output | Render first: helm template | Plain YAML by design |
| Best for | Third-party and shared charts | Your own app's env changes |

**HELM** (Charts with version history): Renders templates with your values, packaged as a versioned chart.

```bash
helm upgrade -f values.yaml
```

**KUSTOMIZE** (Plain YAML, patched per env): Applies plain YAML with per-environment patches layered on top.

```bash
kubectl apply -k overlays/prod
```

- Helm → package once, install anywhere.
- Kustomize → one base, an overlay per environment.

## Explained

### How they differ

Helm is a template engine plus a package format. You write templates with variables, set defaults in `values.yaml`, and override per environment. The result is a chart: a versioned artefact you can publish to a registry and install anywhere.

Kustomize is not a template engine. You keep plain YAML and describe the changes as patches and overlays: a base, then overlays/prod that edits it. `kubectl apply -k` reads it directly, so nothing extra is installed.

### Where Helm wins

Packaging. A chart carries templates, defaults, version history and a rollback. If you install third-party software, Helm is the standard.  
Review. A values file is small and readable, and the template logic stays in the chart where it belongs.

### Where Kustomize wins

Plain YAML. What you apply is what you can read, with no templating language to debug.  
Small differences. Changing replicas, image tags or limits per environment is a three-line patch.

The honest answer: use Helm to package and ship, Kustomize to adapt a base per environment. Helm can render to stdout, and Kustomize can consume the result.

> **The rule:** choose per layer, not per company.

Templates or patches.
