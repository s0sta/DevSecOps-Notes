---
id: p570
title: "An image pin report in Python"
slug: an-image-pin-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Kubernetes, Containers, Python, DevSecOps, SupplyChain]
source: "LinkedIn post P570 · PythonSec series"
linkedin_date: 2030-05-19
design: code
script: image_pin_report.py
---

# An image pin report in Python

`kubectl get pods -A -o json` returns every image in the cluster, and somewhere in that list is a latest tag that was meant to be temporary. The dump is the inventory; the check is a short parse.

## Quick reference

The full script is at the end of this note: `image_pin_report.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 image_pin_report.py pods.json
```

**Example output**

```text
UNPINNED shop nginx:latest
NS {'shop': 1} TOTAL 1
```

## Explained

### What it does

The script walks every pod and every container. It extracts the tag from the last path segment, so registry ports do not confuse it. An image with a digest is pinned. An image with a tag other than latest is pinned. An image with latest, or with no tag at all, is unpinned and printed with its namespace. The last line counts findings per namespace.

### The run

The output above names one image in shop and reports NS {'shop': 1} TOTAL 1. Exit 0 means every image is pinned, 1 means at least one is not, 2 means the JSON or the shape was wrong.

### Why it matters

latest is a moving reference: the pod that starts tomorrow can run different bytes from the pod you reviewed. No tag means latest by default, which is the same problem with less typing. A digest names the bytes, and a version tag names a promise that the registry can still overwrite.

> **The honest caveat:** a pinned tag can be moved, so this checks the reference, not the bytes. Pair it with a digest policy if you need the image itself to be immutable.

> **The lesson:** pin the reference, then verify what it resolves to.

## In one line

> **A tag moves; a digest does not.** Pin the reference, then check what it resolves to.

**Pin by digest**

```bash
kubectl get pods -A -o json
```

## Script: image_pin_report.py

Download: [scripts/image_pin_report.py](../scripts/image_pin_report.py)

```python
#!/usr/bin/env python3
"""image_pin_report.py - report container images without a tag or digest.

Reads `kubectl get pods -A -o json`, walks every container, and prints each
image that is unpinned: `:latest` or no tag at all. An image with a digest
(`@sha256:...`) is pinned, and so is an image with any other tag. It prints
one line per unpinned image, a per-namespace count, and exits 1 if it found
any.

Usage:
    kubectl get pods -A -o json > /tmp/pods.json
    python3 image_pin_report.py /tmp/pods.json
    kubectl get pods -A -o json | python3 image_pin_report.py -
    python3 image_pin_report.py --help

CI (block a manifest that reintroduces latest):
    python3 image_pin_report.py /tmp/pods.json || exit 1

Cron (weekly drift report):
    0 8 * * 1 kubectl get pods -A -o json | python3 /opt/s0sta/image_pin_report.py - >> /var/log/image-pins.log

Exit codes: 0 every image is pinned, 1 at least one is unpinned,
2 usage or unreadable/invalid input.

Read-only: reads a JSON dump; it does not call the API server, pull an image
or change a workload. A tag can be moved later, so this checks the reference,
not the bytes that run.

By s0sta.com
"""
import argparse
import json
import sys


def load(path):
    """Read a kubectl JSON document and return its items list."""
    try:
        if path == "-":
            document = json.load(sys.stdin)
        else:
            with open(path, "r", encoding="utf-8") as handle:
                document = json.load(handle)
    except OSError as exc:
        raise ValueError("%s: %s" % (path, exc))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("%s: not valid JSON: %s" % (path, exc))
    if not isinstance(document, dict):
        raise ValueError("%s: expected a JSON object" % path)
    if not isinstance(document.get("items"), list):
        raise ValueError("%s: expected an items array" % path)
    return document["items"]


def tag_of(image):
    """Return the tag of a reference, or an empty string when it has none."""
    if "@" in image:
        return ""
    last = image.rsplit("/", 1)[-1]
    if ":" in last:
        return last.rsplit(":", 1)[1]
    return ""


def unpinned(image):
    """True when the reference is latest or has no tag at all."""
    if "@" in image:
        return False
    return tag_of(image) in ("", "latest")


def containers(pod):
    """Yield every container image in one pod, including init containers."""
    spec = pod.get("spec")
    if not isinstance(spec, dict):
        raise ValueError("pod has no spec object")
    for field in ("containers", "initContainers"):
        entries = spec.get(field) or []
        if not isinstance(entries, list):
            raise ValueError("pod %s is not a list" % field)
        for container in entries:
            if not isinstance(container, dict):
                raise ValueError("container entry is not an object")
            image = container.get("image")
            if isinstance(image, str) and image:
                yield image


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report Kubernetes images that use latest or no tag.")
    parser.add_argument("pods", nargs="?", default="-",
                        help="kubectl JSON file; stdin when omitted")
    args = parser.parse_args(argv)
    try:
        pods = load(args.pods)
    except ValueError as exc:
        print("image_pin_report: %s" % exc, file=sys.stderr)
        return 2
    counts = {}
    total = 0
    try:
        for pod in pods:
            if not isinstance(pod, dict):
                raise ValueError("pod entry is not an object")
            metadata = pod.get("metadata")
            if not isinstance(metadata, dict):
                raise ValueError("pod has no metadata object")
            namespace = metadata.get("namespace") or "default"
            for image in containers(pod):
                if unpinned(image):
                    total += 1
                    counts[namespace] = counts.get(namespace, 0) + 1
                    print("UNPINNED %s %s" % (namespace, image))
    except ValueError as exc:
        print("image_pin_report: %s" % exc, file=sys.stderr)
        return 2
    summary = {name: counts[name] for name in sorted(counts)}
    print("NS %s TOTAL %d" % (summary, total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
```
