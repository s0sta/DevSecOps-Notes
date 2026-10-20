---
id: p223
title: "Anatomy of a helm upgrade"
slug: anatomy-of-a-helm-upgrade
sections: [devsecops]
topic: "GitOps & Helm"
tags: [Helm, Kubernetes, GitOps, DevOps, CICD]
source: "LinkedIn post P223 · Platform series"
linkedin_date: 2028-02-29
design: anatomy
---

# Anatomy of a helm upgrade

Helm is how most teams package Kubernetes manifests, and `helm upgrade` is the command that ships a release. Short enough to type from memory, long enough that every part matters when something goes wrong.

## Quick reference

```text
helm upgrade api ./chart --set image.tag=1.4.2 --atomic
```

| Part | Name | What it means |
|:--|:--|:--|
| `helm upgrade` | The verb | Creates a release or updates one. On a first install it fails; `--install` fixes that. |
| `api` | Release name | How Helm tracks this deployment. One release, one name, one history. |
| `./chart` | The chart | A local folder, a repo chart, or an oci:// reference. The templates to render. |
| `--set image.tag=1.4.2` | One value | Fast for a test. For anything repeated, use -f `values-prod.yaml`. |
| `--atomic` | The safety net | Waits for readiness, then rolls the release back if it fails. |

## Explained

The verb. `helm upgrade` creates a release or updates one that already exists. On a first install it fails, which is why most pipelines use upgrade `--install` so the same command works both ways.

The release name. api is how Helm tracks this deployment inside the cluster: one release, one name, one history. Reusing a name across environments is how people overwrite production by accident.

The chart. `./chart` is a local folder. It could also be a repo name or an OCI reference like oci://registry/charts/api. It tells Helm which templates and default values to render.

The inline override. `--set image.tag=1.4.2` changes one value quickly. It is fine for a test. For anything a pipeline repeats, put the value in a values file with -f, where it can be reviewed and diffed.

The safety net. `--atomic` makes Helm wait for the new pods to become ready, and rolls the whole release back if they do not. Without it, a failed upgrade leaves the release half-applied and the next deploy inherits the mess.

> **The lesson:** the last flag is what turns an upgrade from a gamble into a rollback plan.

## In one line

> **Upgrade is a rollback plan.** Without `--atomic`, a failed release stays half-applied.

**Dry run first**

```bash
helm upgrade api ./chart --dry-run
```
