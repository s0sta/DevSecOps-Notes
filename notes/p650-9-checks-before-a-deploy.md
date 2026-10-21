---
id: p650
title: "9 checks before a deploy"
slug: 9-checks-before-a-deploy
sections: [devsecops]
topic: "Git & CI/CD"
tags: [Bash, CICD, Kubernetes, DevOps, SRE]
source: "LinkedIn post P650 · ShellSec series"
linkedin_date: 2030-11-21
design: checklist
---

# 9 checks before a deploy

Nine checks, three groups, one decision. The gate script runs five of them automatically; the other four belong to the artifact and smoke steps.

## Quick reference

### Context

```bash
# Context is production
kubectl config current-context
# Namespace exists
kubectl get ns api -o name
# Kubeconfig is the right one
echo $KUBECONFIG
```

### Artifact

- **Image is pinned by digest** — image@sha256:...
- **Manifest verifies** — `sha256sum -c SHA256SUMS`
- **Every file is present** — `artifact_check.sh`

### Health

- **Previous rollout is green** — `kubectl rollout status`
- **No incident flag is open** — no deploy.block file
- **Smoke list is current** — `curl -fsS $URL/healthz`

## Explained

### Context

The current context is production, not the one the runner had cached. The namespace exists, so the apply does not create a surprise or fail halfway through. The kubeconfig is the one from the environment secret, not the copy on your laptop. If those three disagree, stop and fix the runner before the pipeline starts.

### Artifact

The image is pinned by digest, so a rebuild cannot change what ships. The manifest verifies against the files, so a skipped upload fails here instead of in the cluster. Every expected file is present, including the migration and the config bundle, and the count matches the manifest.

### Health

The previous rollout is green; stacking a release on a broken one hides both. No incident flag is open, because a deploy during an incident adds a second variable. The smoke list is current, points at endpoints that matter, and ran against staging in the last hour.

> **The honest caveat:** a checklist is not a gate until something fails the build. If every item is a person ticking a box, it is a poster with good typography.

> **The lesson:** nine answers, one go or no-go, and the pipeline, not a person, enforces it.

## In one line

> **Nine checks, one go or no-go.** The gate runs five of them for you.

**The first check**

```bash
kubectl config current-context
```
