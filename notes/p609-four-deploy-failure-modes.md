---
id: p609
title: "Four deploy failure modes"
slug: four-deploy-failure-modes
sections: [devsecops]
topic: "Git & CI/CD"
tags: [DevOps, SRE, CICD, Kubernetes, Reliability]
source: "LinkedIn post P609 · PythonFixes series"
linkedin_date: 2030-08-18
design: explainer
---

# Four deploy failure modes

The deploy passed every stage and the error rate tripled. Four failure modes explain almost every version of that sentence.

## Quick reference

### Wrong artifact

- The build uploads a.tar.gz, the deploy pulls b.tar.gz
- A tag moved after the release was approved
- Compare the digest the runtime pulled

### Missing digest

- The manifest names a tag, not a sha256
- The same tag resolves to new bytes tomorrow
- Pin image@sha256 in the Deployment

### No rollback

- revisionHistoryLimit is 0, so old sets are gone
- rollout undo has nothing to scale up
- Keep ten revisions and test one undo

### Silent smoke test

- curl exits 0 on a 500 without `--fail`
- A 200 can come from the old pods
- Assert a value only the new code returns

> **Note:** Four checks; most pipelines run one of them and call it verification.

## Explained

### Wrong artifact

The build uploads one file and the deploy pulls another. Sometimes a retry leaves both names in the bucket, sometimes a tag moved after approval. The fix is a digest, not a filename: compare the bytes the runtime pulled with the bytes the build recorded.

### Missing digest

The manifest names a tag, the cluster resolves it, and the next pull gets different bytes because someone pushed the same tag again. A tag is a pointer. Pin image@sha256 in the Deployment and keep the tag for humans.

### No rollback

revisionHistoryLimit is 0, or the old ReplicaSet was deleted, so rollout undo has nothing to scale up. Keep ten revisions, keep the old images in the registry, and test one undo before you need it.

### Silent smoke test

The step curls the health endpoint without `--fail`, gets a 500, and exits 0. Or it gets a 200 from the pod that never left. A smoke test needs an assertion: a value only the new release returns, checked before traffic moves.

The note at the bottom says most pipelines run one of them and call it verification. A wrong artifact often arrives with a missing digest, and a silent smoke test hides both.

> **The honest caveat:** most real incidents combine two of these, and a checklist long enough to catch all four is a pipeline of its own.

> **The lesson:** name the failure mode before adding another green step.

## In one line

> **Trust the check, not the green.** A deploy is done when the running system says so.

**Verify the pod**

```bash
kubectl get pod api-7d9f -o yaml
```
