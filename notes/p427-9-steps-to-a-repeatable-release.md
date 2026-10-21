---
id: p427
title: "9 steps to a repeatable release"
slug: 9-steps-to-a-repeatable-release
sections: [devsecops]
topic: "Release & build engineering"
tags: [ReleaseEngineering, DevOps, CICD, Kubernetes, Git]
source: "LinkedIn post P427 · DevOps series"
linkedin_date: 2029-06-19
design: steps
---

# 9 steps to a repeatable release

A repeatable release is not a checklist someone remembers; it is the same nine actions, in the same order, every time. Here is the sequence that turns a tag into traffic.

## Quick reference

### Prepare — Freeze, tag, sign

```bash
# Tag the commit that passed CI, not the merge after it.
git tag -a v1.4.0 -m "release 1.4.0"
# One push starts one build, from one commit.
git push origin v1.4.0
# Sign the digest, then promote that digest.
cosign sign --key cosign.key $IMAGE
```

### Ship — Promote the digest

```bash
# The same digest staging tested, no rebuild.
kubectl set image deploy/api api=$IMAGE
# Wait until every replica reports ready.
kubectl rollout status deploy/api
# The production canary starts at 10 percent.
kubectl argo rollouts set image api api=$IMAGE
```

### Verify — Let the numbers decide

```bash
# Canary and stable, error rate and p99.
kubectl argo rollouts get rollout api
# Advance one step, then watch again.
kubectl argo rollouts promote api
# Record what runs, where the next incident starts.
kubectl annotate rollout/api release=v1.4.0
```

## Explained

### Prepare

Tag the commit that passed CI, push the tag so one build starts from one commit, then sign the image digest. The tag names the release; the signature proves the bytes did not change after the build. A rebuild here would make the signature a decoration.

### Ship

Promote the signed digest to staging, wait for every replica to report ready, then set the same digest on the production canary. No step rebuilds, and no step touches a pod by hand. If staging fails, the release stops before production sees a single request, and the tag remains a record of what was attempted.

### Verify

Read the canary against stable: error rate first, then p99 latency. Promote one step at a time, watch again, and annotate the workload with the version that is now running. The annotation is what the next incident starts from, and the next release can compare itself against it.

> **The honest caveat:** these nine steps only hold if the pipeline is the only path to production. One manual kubectl edit and the next release becomes a surprise.

> **The lesson:** the value of nine steps is that step ten, the emergency, looks the same.

## In one line

> **Same steps, every time.** A release you cannot repeat is a release you cannot trust.

**Tag it first**

```bash
git tag -a v1.4.0 -m 'release 1.4.0'
```
