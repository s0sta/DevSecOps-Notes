---
id: p602
title: "Did the deploy actually land?"
slug: did-the-deploy-actually-land
sections: [devsecops]
topic: "Python scripts"
tags: [Kubernetes, CICD, DevOps, Python, Deployment]
source: "LinkedIn post P602 · PythonFixes series"
linkedin_date: 2030-08-01
design: code
script: deploy_verify.py
---

# Did the deploy actually land?

A release goes green at 21:40 and the on-call engineer closes the tab. At 22:05 a customer sees last week's price, because one pod still runs the old image and the Service keeps sending it traffic.

## Quick reference

The full script is at the end of this note: `deploy_verify.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 deploy_verify.py /tmp/pods.json release.json
```

**Example output**

```text
FINDING 2 pod problems
ALERT ready 2 of 3
```

## Explained

### What it does

`deploy_verify.py` reads kubectl get pods -o json and a release file with image, digest, replicas and max_age_minutes. It strips the tag, compares the digest with each container's imageID, counts pods that are Running with every container Ready, and flags pods older than the window. A stale pod is one the rollout never replaced.

### What the screen shows

The fourteen lines load pods and the digest, then walk each pod. They add its Ready bit, strip the Z from creationTimestamp, mark stale after 30 minutes and compare the digest. The last lines print FINDING 2 pod problems, then ALERT ready 2 of 3, and exit 1.

### How to run it

kubectl get pods -n prod -o json > `/tmp/pods.json`, then `python3 deploy_verify.py /tmp/pods.json release.json`. Run it after the rollout; exit 1 fails the job.

### The fix

Delete the stale pod and re-apply the digest.

### Prevention

Run the check on a ten-minute cron during the rollout. A deploy is finished when the pods say so.

> **The honest caveat:** creationTimestamp is the pod's age, not the container's, so a restarted container can look stale. Run the check inside the rollout window; a stable release is old by design.

> **The lesson:** verify what runs, not what was sent.

## In one line

> **A green build is not a deploy.** The pod says what is running; the pipeline only says what it sent.

**Check the digest:** crane digest ghcr.io/acme/api:v2

## Script: deploy_verify.py

Download: [scripts/deploy_verify.py](../scripts/deploy_verify.py)

```python
#!/usr/bin/env python3
"""Verify that a deployed release is actually running.

Reads a pod dump and a small release file, then checks the three things a
green pipeline cannot tell you:

  * the running image is the expected repository, on the expected digest
  * enough pods are Ready, not merely Running
  * every pod is younger than the release window, so no stale pod is still
    serving traffic from the previous ReplicaSet

The release file is JSON:

    {"image": "ghcr.io/acme/api",
     "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
     "replicas": 3,
     "max_age_minutes": 30,
     "namespace": "prod"}

image is the repository, without a tag. digest is the sha256 the release
should be running. replicas is the number of Ready pods expected. namespace
and max_age_minutes are optional; the defaults are all namespaces and 60
minutes. The digest is compared against status.containerStatuses[].imageID,
which is what the runtime pulled, not what the manifest asked for.

Usage:
    kubectl get pods -n prod -o json > /tmp/pods.json
    python3 deploy_verify.py /tmp/pods.json release.json
    kubectl get pods -n prod -o json | python3 deploy_verify.py - release.json
    python3 deploy_verify.py /tmp/pods.json release.json --max-age-minutes 15

Exit codes: 0 verified, 1 mismatch or stale pod, 2 usage or unreadable,
missing or invalid input.

CI (after a rollout, fail the job when the pods do not match):
    kubectl get pods -n prod -o json > /tmp/pods.json
    python3 deploy_verify.py /tmp/pods.json release.json || exit 1

Cron (every ten minutes during a rollout):
    */10 * * * * kubectl get pods -n prod -o json | python3 /opt/s0sta/deploy_verify.py - /opt/s0sta/release.json

The check is read-only: one file or stdin, no API calls, no writes. It reads
what the kubelet reported. It does not prove the application works; a smoke
test with an assertion does that. A container restart keeps the pod's old
creationTimestamp, so a restarted pod can look older than the release.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class VerifyError(Exception):
    """Anything that should end the run with exit code 2."""


def load_json(source, label):
    """Read JSON from a path, or stdin when source is '-'."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise VerifyError("cannot read %s: %s" % (label, exc))
    except ValueError as exc:
        raise VerifyError("%s is not valid JSON: %s" % (label, exc))


def pod_items(doc):
    """Return the pod list from a List, a single Pod or a plain list."""
    if isinstance(doc, list):
        return doc
    if not isinstance(doc, dict):
        raise VerifyError("the pods file must be a JSON object or list")
    items = doc.get("items")
    if items is not None:
        if not isinstance(items, list):
            raise VerifyError("pods.items must be a list")
        return items
    if doc.get("kind") == "Pod" or ("metadata" in doc and "status" in doc):
        return [doc]
    raise VerifyError("the pods file has no items list and is not a Pod")


def release_spec(doc):
    """Validate and return (image, digest, replicas, max_age, namespace)."""
    if not isinstance(doc, dict):
        raise VerifyError("the release file must be a JSON object")
    image = doc.get("image")
    digest = doc.get("digest")
    replicas = doc.get("replicas")
    max_age = doc.get("max_age_minutes", 60)
    namespace = doc.get("namespace")
    if not isinstance(image, str) or not image.strip():
        raise VerifyError("release.image must be a non-empty string")
    if not isinstance(digest, str) or not DIGEST_RE.match(digest.lower()):
        raise VerifyError("release.digest must be sha256:<64 hex characters>")
    if isinstance(replicas, bool) or not isinstance(replicas, int) or replicas < 0:
        raise VerifyError("release.replicas must be a non-negative integer")
    if isinstance(max_age, bool) or not isinstance(max_age, int) or max_age <= 0:
        raise VerifyError("release.max_age_minutes must be a positive integer")
    if namespace is not None and (not isinstance(namespace, str) or not namespace):
        raise VerifyError("release.namespace must be a non-empty string")
    return image.strip(), digest.lower(), replicas, max_age, namespace


def image_repo(ref):
    """Return the repository part of an image reference, without tag or digest."""
    ref = ref.split("@", 1)[0]
    slash = ref.rfind("/")
    colon = ref.rfind(":")
    if colon > slash:
        return ref[:colon]
    return ref


def parse_time(value, label):
    """Parse a Kubernetes RFC 3339 timestamp into an aware UTC datetime."""
    if not isinstance(value, str) or not value:
        raise VerifyError("%s is missing" % label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise VerifyError("%s is not a timestamp: %s" % (label, value))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def as_dict(value, label):
    """Return a mapping, raising on the wrong shape."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise VerifyError("%s must be an object" % label)
    return value


def pod_report(pod, number, expected_repo, digest, max_age, namespace, now):
    """Return (ready, problems) for one pod, printing one FAIL line each."""
    metadata = as_dict(pod.get("metadata"), "pod %d metadata" % number)
    name = metadata.get("name") or "pod-%d" % number
    if namespace and metadata.get("namespace") != namespace:
        return None, 0
    status = as_dict(pod.get("status"), "pod %s status" % name)
    containers = status.get("containerStatuses")
    if containers is None:
        containers = []
    if not isinstance(containers, list):
        raise VerifyError("pod %s containerStatuses must be a list" % name)
    created = parse_time(metadata.get("creationTimestamp"),
                         "pod %s creationTimestamp" % name)
    age = now - created
    problems = 0
    for index, container in enumerate(containers, 1):
        container = as_dict(container, "pod %s container %d" % (name, index))
        image = container.get("image")
        image_id = container.get("imageID")
        if not isinstance(image, str) or image_repo(image) != expected_repo:
            print("FAIL pod %s image %s" % (
                name, image if isinstance(image, str) else "missing"))
            problems += 1
        elif not isinstance(image_id, str) or digest not in image_id:
            print("FAIL pod %s digest" % name)
            problems += 1
    if age > timedelta(minutes=max_age):
        print("FAIL pod %s stale %dm" % (name, int(age.total_seconds() // 60)))
        problems += 1
    ready = (status.get("phase") == "Running" and bool(containers)
             and all(c.get("ready") is True for c in containers))
    return ready, problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify running pods against an expected image digest, "
                    "replica count and age window.",
        epilog="Exit codes: 0 verified, 1 mismatch, 2 usage or input error.")
    parser.add_argument("pods", help="kubectl get pods -o json output, or - for stdin")
    parser.add_argument("release", help="release JSON with image, digest and replicas")
    parser.add_argument("--max-age-minutes", type=int, default=None,
                        help="override release.max_age_minutes (default 60)")
    args = parser.parse_args(argv)

    try:
        image, digest, replicas, max_age, namespace = release_spec(
            load_json(args.release, "release file"))
        if args.max_age_minutes is not None:
            if args.max_age_minutes <= 0:
                raise VerifyError("--max-age-minutes must be positive")
            max_age = args.max_age_minutes
        now = datetime.now(timezone.utc)
        expected_repo = image_repo(image)
        ready_count = 0
        problems = 0
        for number, pod in enumerate(pod_items(load_json(args.pods, "pods file")), 1):
            if not isinstance(pod, dict):
                raise VerifyError("pod %d is not an object" % number)
            ready, pod_problems = pod_report(
                pod, number, expected_repo, digest, max_age, namespace, now)
            if ready is None:
                continue
            if ready:
                ready_count += 1
            problems += pod_problems
    except VerifyError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    short = digest[:19]
    if problems:
        print("FINDING %d pod problems" % problems)
    if ready_count != replicas:
        print("ALERT ready %d of %d" % (ready_count, replicas))
        return 1
    if problems:
        return 1
    print("OK %d of %d ready on %s" % (ready_count, replicas, short))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
