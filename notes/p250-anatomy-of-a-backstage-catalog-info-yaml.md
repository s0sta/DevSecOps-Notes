---
id: p250
title: "Anatomy of a Backstage catalog-info.yaml"
slug: anatomy-of-a-backstage-catalog-info-yaml
sections: [devsecops]
topic: "Platform engineering"
tags: [Backstage, PlatformEngineering, DevOps, Kubernetes, CloudNative]
source: "LinkedIn post P250 · Platform series"
linkedin_date: 2028-05-02
design: anatomy
---

# Anatomy of a Backstage catalog-info.yaml

A `catalog-info.yaml` is a short YAML file, and it decides whether a service exists to everyone outside its repo. Backstage reads it, indexes it and shows it on a page. A missing field fails at processing, not at build.

## Quick reference

```text
apiVersion kind metadata.name spec.type spec.owner spec.lifecycle
```

| Part | Name | What it means |
|:--|:--|:--|
| `apiVersion` | The schema | `backstage.io/v1alpha1` is the current version for catalog entities. |
| `kind` | The entity type | Component for a service or website. Also API, System, Domain, Resource. |
| `metadata.name` | The unique name | Unique for its `kind`. Other entities use it to reference this one. |
| `spec.type` | The type | service, website or library. A custom type is a taxonomy decision. |
| `spec.owner` | The owner | Prefer a group, for example group:default/platform. |
| `spec.lifecycle` | The lifecycle | production, experimental or deprecated. It drives scorecards. |

## Explained

### The six fields

apiVersion. `backstage.io/v1alpha1` is the current version for catalog entities. It is not v1; the alpha is part of the string.  
`kind`. Component for a service, website or library. The same schema covers API, System, Domain and Resource.  
`metadata.name`. The unique name of the entity within its `kind`. Other entities use it to reference this one, so renaming it breaks those references.  
`spec.type`. service, website or library. The catalog accepts any string, but a custom type is a taxonomy decision.  
`spec.owner`. The owning group, for example group:default/platform. Prefer a group to a person; groups outlive staff changes.  
`spec.lifecycle`. production, experimental or deprecated. It tells readers whether the service is safe to depend on.

### What goes wrong

An owner that does not resolve shows up as an orphan, and a missing required field keeps the entity out of the catalog. Both pass the commit and surface when Backstage processes the entity.

> **The honest caveat:** Backstage validates the entity when it processes it, not when you push. A typo in an owner can sit in Git for weeks.

> **The lesson:** the catalog is only as true as the owner and lifecycle you put in it.

## In one line

> **A file is not a service.** The catalog only works when owner and lifecycle are true.

**Lint the file**

```bash
yamllint catalog-info.yaml
```
