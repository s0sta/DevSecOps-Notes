---
id: p208
title: "9 skills to have ready for the CKA exam"
slug: 9-skills-to-have-ready-for-the-cka-exam
sections: [devsecops]
topic: "Kubernetes"
tags: [Kubernetes, CKA, DevOps, CloudNative, Certification]
source: "LinkedIn post P208 · Cloud / DevSecOps series"
linkedin_date: 2028-01-25
design: checklist
---

# 9 skills to have ready for the CKA exam

The CKA is hands-on and timed: you fix real clusters in a terminal, with the Kubernetes docs open. Theory is not enough; speed is the skill. Nine things to have in muscle memory before exam day.

## Quick reference

### Speed

- **alias k=kubectl** — and k get po -A by reflex
- **Generate YAML** — `--dry-run=client -o yaml`
- **Find docs fast** — kubernetes.io/docs is open in the exam

### Core tasks

- **Fix a broken pod** — logs `--previous`, describe
- **Expose a deployment** — `kubectl expose + test`
- **RBAC + service accounts** — create role, rolebinding

### Cluster

```bash
# Drain and cordon a node
kubectl drain <node>
# etcd backup and restore
etcdctl snapshot save
# Set the right context
kubectl config use-context
```

## Explained

### Speed

alias k=kubectl, set at the start, saves keystrokes on every command. k get po -A should be automatic.  
Generate YAML with `--dry-run=client -o yaml` instead of writing it by hand. This alone saves minutes per question.  
Find docs fast. kubernetes.io is allowed during the exam, so practise searching it quickly for the one YAML snippet you need, rather than memorising everything.

### Core tasks

Fix a broken pod: `kubectl logs --previous` and kubectl describe, then correct the cause. Troubleshooting is the biggest chunk of the exam.  
Expose a deployment with a service and verify it works from another pod.  
RBAC: create a role and rolebinding, and a service account, and test what it can and cannot do.

### Cluster

Drain and cordon a node for maintenance with kubectl drain, then uncordon it.  
etcd backup and restore with `etcdctl snapshot save` and restore. A classic, high-value question.  
Set the right context first. Every task tells you which cluster to use; `kubectl config use-context` is the first thing you run, every question, or you will fix the wrong cluster.

The mindset: the CKA rewards the person who has done these tasks a hundred times, not the one who has read about them. Build a kind or k3s cluster and break it on purpose.

## In one line

> **The CKA tests speed, not theory.** It is hands-on and timed. Practise until it is reflex.

**Always first**

```bash
kubectl config use-context <q>
```
