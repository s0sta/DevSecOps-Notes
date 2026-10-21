---
id: p447
title: "9 steps to a preview environment"
slug: 9-steps-to-a-preview-environment
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, Kubernetes, CICD, GitOps, PlatformEngineering]
source: "LinkedIn post P447 · DevOps series"
linkedin_date: 2029-08-05
design: steps
---

# 9 steps to a preview environment

A reviewer opens pull request 142 and asks for a demo. Ten minutes later the branch is running at its own URL, with data, and the link is in the thread. That is a preview environment: a lifecycle, not a server.

## Quick reference

### Create — Give the pull request a home

```bash
# The pipeline names the preview after the PR number.
git push origin feature/checkout
# One namespace fences the preview from every other.
kubectl create ns pr142
# The staging chart, with a preview values file.
helm upgrade --install pr142 ./chart -n pr142
```

### Seed — Make it look like a real system

```bash
# Synthetic fixtures, never a production copy.
pg_restore -d preview seed.dump
# The same schema version as staging, not a guess.
python3 manage.py migrate
# Fail the job if the app does not answer.
curl -fsS $PREVIEW_URL/health
```

### Destroy — Take it down when the PR closes

```bash
# Remove the release, not only the running pods.
helm uninstall pr142 -n pr142
# The namespace takes secrets and volumes with it.
kubectl delete ns pr142
# Uploads and test artefacts live outside the cluster.
aws s3 rm s3://previews/pr142 --recursive
```

## Explained

### Create

1. **Push the branch.** The pipeline names the environment after the pull request number, so two previews never collide.
   \2. Create the namespace. One namespace per preview fences its deployment, service, ingress and secrets from other previews.
   \3. Install the chart. The same chart as staging, with a values file that points at the preview database and a lower replica count. The ingress prints the URL.

### Seed

4. **Restore the seed dump.** Synthetic fixtures, never a production copy; the point is realistic shapes without real people.
   \5. Run the migrations. The preview database starts at the same schema version as staging.
   \6. Hit the health endpoint. `curl -fsS` on /health fails the job if the app does not answer, so a broken preview is never announced.

### Destroy

7. **Uninstall the release.** helm uninstall removes the objects the chart owns.
   \8. Delete the namespace. It takes the service, ingress, secrets and volumes with it.
   \9. Delete the bucket prefix. Uploads and test artefacts live outside the cluster, so the sweep has to include object storage.

> **The honest caveat:** previews cost money and abandoned ones rot. Add a scheduled sweeper that deletes any preview older than seven days, or the webhook will eventually fail and leave one behind.

> **The lesson:** the value of a preview is that it disappears.

## In one line

> **A preview is a lease, not a server.** Create it, seed it, and take it down when the pull request closes.

**Destroy on close**

```bash
gh pr close 142 --delete-branch
```
