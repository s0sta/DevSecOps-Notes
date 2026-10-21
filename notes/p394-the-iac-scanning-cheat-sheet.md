---
id: p394
title: "The IaC scanning cheat sheet"
slug: the-iac-scanning-cheat-sheet
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [DevSecOps, IaC, Terraform, Kubernetes, CloudNative]
source: "LinkedIn post P394 · DevSecOps series"
linkedin_date: 2029-04-03
design: cheatsheet
---

# The IaC scanning cheat sheet

Terraform, Kubernetes and a Dockerfile can all be wrong in ways a plan will not show. Four scanners, run in order, cover the infrastructure before it is applied.

## Quick reference

### Terraform

```bash
checkov -d . --framework terraform
trivy config .
terraform validate
terraform plan -out tfplan
checkov -d . --compact
```

### Kubernetes

```bash
kubectl apply --dry-run=server -f .
kubectl auth can-i --list
kubectl get sa -A -o wide
kubectl get pods -A
kube-score score deploy.yaml
```

### Containers

```bash
trivy image api:1.4.2
trivy image --severity HIGH api:1.4.2
trivy image --exit-code 1 api:1.4.2
hadolint Dockerfile
docker scout cves api:1.4.2
```

### Policy

```bash
conftest test -p policy deploy.yaml
conftest verify
opa eval -d policy 'data.main.deny'
checkov -d . --framework kubernetes
kyverno apply policy/ -r .
```

## Explained

### Terraform

Start with `terraform validate`, which parses the configuration without touching state. `checkov -d . --framework terraform` checks the resources against its policy set: public buckets, open security groups, unencrypted disks. `trivy config .` scans the same files and prints the offending line.

### Kubernetes

`kubectl apply --dry-run=server -f .` asks the API server to validate the manifest without persisting it, which catches schema errors a local lint misses. `kubectl auth can-i --list` shows what the current identity can do. kube-score score `deploy.yaml` grades the workload on probes, limits and security context.

### Containers

`trivy image api:1.4.2` lists CVEs in the image layers. `trivy image --exit-code 1 api:1.4.2` turns the same scan into a gate. `hadolint Dockerfile` checks the build file itself, and `docker scout cves api:1.4.2` gives a second opinion on the same image.

### Policy

`conftest test -p policy deploy.yaml` runs your own Rego rules against the manifest. `conftest verify` checks those rules before they check anything else. `opa eval -d policy 'data.main.deny'` shows what the policy returns, and `checkov -d . --framework kubernetes` adds its built-in checks.

> **The honest caveat:** a scanner only finds the rules someone wrote, and a clean report is not proof of a safe configuration.

> **The lesson:** scan the source, test the policy, and gate the apply.

## In one line

> **Scan before you apply.** A clean plan can still be an unsafe configuration.

**Scan the source**

```bash
trivy config .
```
