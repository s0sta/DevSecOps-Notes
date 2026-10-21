---
id: p543
title: "Querying cloud JSON without an SDK"
slug: querying-cloud-json-without-an-sdk
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [Python, AWS, Kubernetes, CloudCLI, DevSecOps]
source: "LinkedIn post P543 · PythonSec series"
linkedin_date: 2030-03-17
design: cheatsheet
---

# Querying cloud JSON without an SDK

You need every unencrypted volume, and the SDK wants credentials, a client and a paginator first. The CLI already prints JSON; the gap is the query.

## Quick reference

### Select

```bash
aws sts get-caller-identity
jq '.items[].metadata.name' pods.json
kubectl get cm -o jsonpath='{.data}'
python3 -m json.tool ec2.json
aws s3api list-buckets --query 'Buckets'
```

### Filter

```bash
jq '.Volumes[]|select(.Encrypted==false)'
jq '.Users[]|select(.PasswordLastUsed)'
jq '.Statement[]|select(.Effect=="Allow")'
jq '.Grants[]|select(.Grantee.URI)'
```

### Aggregate

```bash
jq '.items | length' pods.json
jq '[.Volumes[].Size] | add' vols.json
jq '[.items[].spec.containers[]] | length'
jq 'group_by(.region) | map(length)'
```

### Diff

```bash
jq -S . old.json > /tmp/a.json
jq -S . new.json > /tmp/b.json
diff -u /tmp/a.json /tmp/b.json
kubectl diff -f deploy.yaml
jq -S . policy.json | sha256sum
```

## Explained

### Four moves

Select. Ask for the field, not the object. `aws sts get-caller-identity` proves the account. `jq '.items[].metadata.name' pods.json` lists pod names, `kubectl get cm -o jsonpath='{.data}'` prints a config map, `python3 -m json.tool ec2.json` makes a response readable, and `aws s3api list-buckets --query 'Buckets'` lists buckets.

Filter. Keep only matching objects. `jq '.Volumes[]|select(.Encrypted==false)'` finds unencrypted volumes, .Users[]|select(.PasswordLastUsed) finds console sign-ins, .Statement[]|select(.Effect=="Allow") keeps allow statements, and .Grants[]|select(.Grantee.URI) finds ACL grants.

Aggregate. Count and group. jq '.items | length' counts pods, [.Volumes[].Size] | add sums volume sizes, [.items[].spec.containers[]] | length counts containers, and group_by(.region) | map(length) counts objects per region.

Diff. Sort both sides first. `jq -S . old.json > /tmp/a.json` and the same for the new file, then diff -u the two. `kubectl diff -f deploy.yaml` compares a manifest with the live object, and `jq -S . policy.json | sha256sum` checks equality.

### The glue

Python is the glue: subprocess.run captures the output, json.loads parses it, and a threshold becomes exit 1. Python keeps types honest: counts stay integers, booleans stay booleans, and an empty list is not a missing key.

> **The honest caveat:** none of these reduces the payload. `--query` filters after the response arrives, jq is another dependency on the runner, and jsonpath prints text rather than JSON.

> **The lesson:** query the shape at the edge, then let Python decide.

## In one line

> **Ask the JSON, not the SDK.** The query is cheap; the parsing is where the bugs live.

**Pretty-print one**

```bash
python3 -m json.tool ec2.json
```
