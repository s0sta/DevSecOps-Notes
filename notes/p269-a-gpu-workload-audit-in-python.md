---
id: p269
title: "A GPU workload audit in Python"
slug: a-gpu-workload-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [GPU, Kubernetes, Python, DevSecOps, SRE]
source: "LinkedIn post P269 · Platform series"
linkedin_date: 2028-06-15
design: code
script: gpu_audit.py
---

# A GPU workload audit in Python

You run `kubectl get pods -A -o json` and get a page of JSON. Somewhere in it are the pods holding the expensive cards, and some of them are privileged, run latest, or mount the node filesystem.

## Quick reference

The full script is at the end of this note: **gpu_audit.py** (standard library only, no `pip install`).

**Run it**

```bash
kubectl get pods -A -o json | python3 gpu_audit.py -
```

**Example output**

```text
ALERT GPUS 13 FLAGS 2
```

## Explained

### What it does

The script reads that dump, finds every container that requests an `nvidia.com/gpu`, and checks the pod around it: is the image pinned to a tag that is not latest, do the containers have CPU and memory limits, is anything privileged, and does the pod mount a hostPath volume. It prints the GPU inventory, one line per finding, and exits 1 if there are any.

### Why these four

A GPU pod holds model weights, which are data you may not want on a shared host. A hostPath mount turns that into host access, privileged mode removes the container boundary, and no limits let one pod starve the node. An unpinned image means the code that runs tomorrow is not the code you reviewed.

### How to use it

Export the pods and pipe them in: `kubectl get pods -A -o json | python3 gpu_audit.py -`. Run it against a saved dump in CI, or nightly against the live cluster. A clean run prints OK and exits 0.

> **The honest caveat:** the device plugin is the source of truth for allocation, and a pod that requests a GPU may sit Pending. This audits configuration, not utilisation, so pair it with DCGM metrics for the other half.

> **The lesson:** a GPU is a node-level asset. Treat the pods that hold one like node-level workloads.

## In one line

> **A GPU pod is still a pod.** The same hardening rules, plus an expensive queue.

**Audit now**

```bash
kubectl get pods -A -o json
```

## Script: gpu_audit.py

Download: [scripts/gpu_audit.py](../scripts/gpu_audit.py)

```python
#!/usr/bin/env python3
"""gpu_audit.py - audit the Kubernetes pods that request GPUs.

Reads `kubectl get pods -A -o json` from a file or stdin. For every pod that
asks for a GPU it reports the card count, then checks the four things that
turn a GPU workload into a host-wide risk:

    image pinned        a digest, or a tag that is not :latest
    cpu and memory      limits on every container
    privileged          container securityContext.privileged is false
    hostPath            no volume mounts the node filesystem

Read-only: it only parses JSON and never talks to the cluster. Exit codes:
0 clean, 1 finding, 2 usage or read error.

Usage:
    kubectl get pods -A -o json | python3 gpu_audit.py -
    python3 gpu_audit.py pods.json
    python3 gpu_audit.py pods.json --namespace ml
    python3 gpu_audit.py pods.json --all --json

Cron (nightly at 03:00):
    0 3 * * * kubectl get pods -A -o json | python3 gpu_audit.py - >> /var/log/gpu_audit.log 2>&1

By s0sta.com
"""
import argparse
import json
import sys

GPU_KEYS = ("nvidia.com/gpu", "amd.com/gpu")


def gpu_count(container):
    """Cards requested by one container, 0 when it requests none."""
    resources = container.get("resources") or {}
    best = 0
    for part in ("requests", "limits"):
        for key in GPU_KEYS:
            value = (resources.get(part) or {}).get(key)
            try:
                best = max(best, int(value))
            except (TypeError, ValueError):
                pass
    return best


def pinned(image):
    """True when the image is a digest or a tag that is not latest."""
    if "@sha256:" in image:
        return True
    tail = image.rsplit("/", 1)[-1]
    return ":" in tail and not tail.endswith(":latest")


def has_limits(container):
    limits = (container.get("resources") or {}).get("limits") or {}
    return bool(limits.get("cpu")) and bool(limits.get("memory"))


def is_privileged(container):
    context = container.get("securityContext") or {}
    return context.get("privileged") is True


def host_paths(pod):
    """Names of volumes that mount a path from the node."""
    spec = pod.get("spec") or {}
    return [volume.get("name", "?") for volume in spec.get("volumes") or []
            if "hostPath" in volume]


def check_pod(pod, scan_all=False):
    """Return (namespace, name, cards, findings) or None if skipped."""
    meta = pod.get("metadata") or {}
    namespace = meta.get("namespace", "default")
    name = meta.get("name", "?")
    spec = pod.get("spec") or {}
    containers = spec.get("containers") or []
    cards = sum(gpu_count(container) for container in containers)
    if cards == 0 and not scan_all:
        return None

    findings = []
    for container in containers:
        cname = container.get("name", "?")
        image = str(container.get("image", ""))
        if not pinned(image):
            findings.append((namespace, name, cname, "unpinned image", image))
        if not has_limits(container):
            findings.append((namespace, name, cname, "no cpu/memory limits", ""))
        if is_privileged(container):
            findings.append((namespace, name, cname, "privileged container", ""))
    for volume in host_paths(pod):
        findings.append((namespace, name, "-", "hostPath volume", volume))
    return namespace, name, cards, findings


def load_pods(path, errors):
    """Load the items list from one kubectl JSON dump."""
    label = "<stdin>" if path == "-" else path
    try:
        if path == "-":
            doc = json.load(sys.stdin)
        else:
            with open(path, "r", encoding="utf-8") as handle:
                doc = json.load(handle)
    except OSError as exc:
        errors.append("%s: %s" % (label, exc))
        return []
    except ValueError as exc:
        errors.append("%s: not JSON: %s" % (label, exc))
        return []
    items = doc.get("items") if isinstance(doc, dict) else None
    if not isinstance(items, list):
        errors.append('%s: expected {"items": [...]} from kubectl -o json' % label)
        return []
    return items


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Audit GPU pods for unpinned images, missing limits, "
                    "privileged containers and hostPath mounts.")
    ap.add_argument("paths", nargs="*", default=["-"], metavar="PATH",
                    help="kubectl JSON dump, or - for stdin (default)")
    ap.add_argument("-n", "--namespace", help="only this namespace")
    ap.add_argument("-a", "--all", action="store_true",
                    help="audit every pod, not only GPU pods")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="findings and summary only")
    ap.add_argument("--json", action="store_true",
                    help="print one machine-readable JSON object")
    args = ap.parse_args(argv)

    errors = []
    audited = []
    for path in args.paths:
        for pod in load_pods(path, errors):
            if not isinstance(pod, dict):
                continue
            result = check_pod(pod, args.all)
            if result is None:
                continue
            namespace = result[0]
            if args.namespace and namespace != args.namespace:
                continue
            audited.append(result)

    for message in errors:
        print("error: %s" % message, file=sys.stderr)
    if errors:
        return 2

    findings = [item for _, _, _, items in audited for item in items]
    cards = sum(item[2] for item in audited)
    pods_with_findings = sum(1 for _, _, _, items in audited if items)

    if args.json:
        print(json.dumps({
            "pods": len(audited),
            "cards": cards,
            "pods_with_findings": pods_with_findings,
            "findings": [
                {"namespace": ns, "pod": pod, "container": container,
                 "check": check, "detail": detail}
                for ns, pod, container, check, detail in findings
            ],
        }, sort_keys=True))
        return 1 if findings else 0

    if not audited:
        print("no GPU pods found" if not args.all else "no pods found")
        return 0

    if not args.quiet:
        for namespace, name, pod_cards, _ in audited:
            print("%-44s %4d GPU" % (namespace + "/" + name, pod_cards))
        for namespace, name, container, check, detail in findings:
            where = "%s/%s" % (namespace, name)
            if container != "-":
                where += " " + container
            extra = " (%s)" % detail if detail else ""
            print("[FINDING] %s: %s%s" % (where, check, extra))
        print()

    print("%d pod(s) audited, %d card(s) requested, %d finding(s)"
          % (len(audited), cards, len(findings)))
    if findings:
        print("ALERT %d of %d pod(s) need review"
              % (pods_with_findings, len(audited)))
        return 1
    print("OK clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
