---
id: p608
title: "Deployment verification commands"
slug: deployment-verification-commands
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Kubernetes, DevOps, CICD, SRE, CommandLine]
source: "LinkedIn post P608 · PythonFixes series"
linkedin_date: 2030-08-15
design: cheatsheet
---

# Deployment verification commands

A release is done and someone asks the only question that matters: is the new version actually serving traffic? Four blocks of commands answer it.

## Quick reference

### Image

```bash
kubectl get deploy api -o yaml
kubectl rollout history deploy/api
kubectl get rs -o wide
docker inspect api | grep -i digest
aws ecr list-images --repository-name api
```

### Pods

```bash
kubectl get pods -l app=api -o wide
kubectl describe pod api-7d9f
kubectl top pod -l app=api
kubectl logs deploy/api --tail=50
```

### Traffic

```bash
kubectl get svc api -o wide
kubectl get endpoints api
kubectl get ingress api -o yaml
curl -sS https://api.example.com/healthz
```

### Rollback

```bash
kubectl rollout undo deploy/api
kubectl rollout status deploy/api
kubectl rollout restart deploy/api
kubectl rollout pause deploy/api
```

## Explained

### Image

Start with the Deployment and its history: the image in the pod template, the revisions the controller kept, and the ReplicaSets still on disk. Docker inspect finds the digest the runtime recorded; the ECR list shows the tags the registry still holds.

### Pods

The pod list with labels shows age and readiness. Describe one pod for its imageID and events, top for the resources it is using, and logs for the version banner or the request it just served.

### Traffic

The Service, its endpoints and the Ingress tell you where requests can go. A curl to the health or version path proves the edge reaches a pod, but only if you read the body. A 200 from the old ReplicaSet is still a 200.

### Rollback

The undo, status, restart and pause commands are the controls. Run rollout history first so you know which revision undo will pick, and run status after the undo so you know it finished rather than started.

Use the blocks in order and save the outputs beside the release record. Prevention is making the same four checks a gate, not a ritual.

> **The honest caveat:** a command that prints a tag or a controller status is not proof of the bytes on the node. Only imageID and the digest answer that.

> **The lesson:** read the running system, then compare it with the release.

## In one line

> **Read the system, not the pipeline.** A command is only a check when you know what a bad answer looks like.

**Check one pod**

```bash
kubectl get pod api-7d9f -o yaml
```
