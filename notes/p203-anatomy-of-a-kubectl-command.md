---
id: p203
title: "Anatomy of a kubectl command"
slug: anatomy-of-a-kubectl-command
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CKA, DevOps, CloudNative, CLI]
source: "LinkedIn post P203 · Cloud / DevSecOps series"
linkedin_date: 2028-01-13
design: anatomy
---

# Anatomy of a kubectl command

Almost every `kubectl` command follows the same shape. Once you see it, the whole CLI becomes predictable, which is exactly what you need under time pressure in the CKA exam.

## Quick reference

```text
kubectl get pods -n shop -o wide
```

| Part | Name | What it means |
|:--|:--|:--|
| `kubectl` | The tool | The CLI that talks to the cluster's API server. |
| `get` | The verb | The action: get, describe, delete, apply, logs. |
| `pods` | The resource | What kind of object: pods, svc, deploy, nodes. |
| `-n shop` | Namespace | Which namespace. Without it, the default one. |
| `-o wide` | Output | The format: wide, yaml, json, or name. |

## Explained

`kubectl` is the tool: the command-line client that talks to your cluster's API server, using the context and credentials in your kubeconfig. `kubectl` config current-context tells you which cluster you are pointed at, worth checking before anything destructive.

get is the verb, the action you want: get to list, describe for detail, logs to read output, apply to create or update, delete to remove, exec to run a command inside a container. Learn the verbs and you can act on anything.

pods is the resource type, the kind of object. It could be pods, svc (services), deploy (deployments), nodes, ns (namespaces) and dozens more. `kubectl` api-resources lists them all, with their short names.

`-n shop` is the namespace flag. Kubernetes divides a cluster into namespaces, and most commands default to the default namespace. Forgetting -n is why people "cannot find" a pod that is really in another namespace. -A targets all namespaces at once.

`-o wide` is the output format. wide adds columns like node and IP; yaml and json give the full object (great for learning and scripting); name gives just names for piping into other commands.

> **The pattern in one line:** `kubectl` verb resource with a namespace and an output format. Master that template and most of `kubectl` is just filling in the blanks.

## In one line

> **Verb, resource, flags.** Every `kubectl` command follows the same shape.

**Learn the shape**

```bash
kubectl <verb> <resource> -n <ns> -o <format>
```
