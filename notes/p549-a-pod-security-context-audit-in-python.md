---
id: p549
title: "A pod security context audit in Python"
slug: a-pod-security-context-audit-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Kubernetes, CloudNative, Python, DevSecOps, CKS]
source: "LinkedIn post P549 · PythonSec series"
linkedin_date: 2030-03-31
design: code
script: k8s_security_context.py
---

# A pod security context audit in Python

The YAML passed review because it was four hundred lines and the diff was two. The pod runs as root, shares the host network and mounts the node filesystem.

## Quick reference

The full script is at the end of this note: `k8s_security_context.py` (standard library only, no `pip install`).

**Run it**

```bash
kubectl get pods -A -o json | python3 k8s_security_context.py -
```

**Example output**

```text
FAIL default web
ALERT 1
```

## Explained

### Six checks

HostNetwork: the pod shares the node network namespace. HostPath: a volume mounts a path from the node. Privileged: a container with securityContext.privileged true. RunAsRoot: the effective runAsUser is 0, after container inheritance. RunAsNonRoot: neither the container nor the pod sets it true. Limits: a container has no resources.limits. A pod can fail several at once, so read the list, not just the count.

### The frame

The condensed version merges the pod security context into each container, checks app and init containers, and prints one FAIL line per pod. On the fixture it prints FAIL default web, then ALERT 1, and exits 1.

### How to run it

`kubectl get pods -A -o json | python3 k8s_security_context.py -`, or save the dump and audit it in CI. Run it nightly against the live cluster and before a release. Exit 0 is clean, 1 is a finding, 2 is an input error.

> **The honest caveat:** it checks configuration, not intent. A CNI or a system add-on may need hostNetwork or privileged, and a missing limit is a risk rather than a breach. Keep an allowlist with an owner.

> **The lesson:** the pod spec is the contract; read it before the node does.

## In one line

> **Root is a choice.** The pod spec says who it runs as and what it can reach.

**Audit the cluster**

```bash
kubectl get pods -A -o json
```

## Script: k8s_security_context.py

Download: [scripts/k8s_security_context.py](../scripts/k8s_security_context.py)

```python
#!/usr/bin/env python3
"""Audit pod security contexts in a kubectl JSON dump.

Reads the output of `kubectl get pods -A -o json` and flags six settings that
turn a pod into a node-level risk:

    privileged          a container runs with securityContext.privileged
    runAsRoot           the effective runAsUser is 0
    runAsNonRoot        neither the container nor the pod sets it to true
    hostPath            a volume mounts a path from the node
    hostNetwork         the pod shares the node network namespace
    no limits           a container has no resources.limits

The effective runAsUser and runAsNonRoot values are inherited: a container
setting wins, otherwise the pod securityContext applies. Both app containers
and init containers are checked. HostPath and hostNetwork are pod-level.

Usage:
    kubectl get pods -A -o json > /tmp/pods.json
    python3 k8s_security_context.py /tmp/pods.json
    kubectl get pods -A -o json | python3 k8s_security_context.py -
    python3 k8s_security_context.py /tmp/pods.json --quiet

Exit codes: 0 no findings, 1 at least one finding, 2 usage, unreadable or
invalid input.

CI (audit a saved dump, fail the job):
    kubectl get pods -A -o json > /tmp/pods.json
    python3 k8s_security_context.py /tmp/pods.json || exit 1
Cron (daily at 06:40):
    40 6 * * * kubectl get pods -A -o json | python3 /opt/s0sta/k8s_security_context.py -

The audit is read-only: it reads one local file or stdin and never calls the
API server. It checks configuration, not exploitability: a system add-on may
need privileged, and a missing limit is a risk, not a breach. Pair it with
Pod Security Admission for enforcement.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys


class AuditError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source):
    """Read the kubectl dump from a file or '-' for stdin."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise AuditError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise AuditError("%s is not JSON: %s" % (source, exc))


def pod_items(doc):
    """Return the pod list from a List, a single Pod, or an items wrapper."""
    if not isinstance(doc, dict):
        raise AuditError("the dump must be a JSON object")
    items = doc.get("items")
    if items is not None:
        if not isinstance(items, list):
            raise AuditError("items must be a list")
        return items
    if doc.get("kind") == "Pod" or ("metadata" in doc and "spec" in doc):
        return [doc]
    raise AuditError("no items list and not a single Pod")


def as_dict(value, label):
    """Return a mapping, or raise when the field has the wrong shape."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise AuditError("%s must be an object" % label)
    return value


def as_list(value, label):
    """Return a list, or raise when the field has the wrong shape."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise AuditError("%s must be a list" % label)
    return value


def effective(container_sc, pod_sc, key):
    """Container securityContext wins; otherwise inherit from the pod."""
    if key in container_sc:
        return container_sc[key]
    return pod_sc.get(key)


def check_pod(pod, number):
    """Return (namespace, name, findings) for one pod."""
    if not isinstance(pod, dict):
        raise AuditError("pod %d is not an object" % number)
    metadata = as_dict(pod.get("metadata"), "pod %d metadata" % number)
    spec = as_dict(pod.get("spec"), "pod %d spec" % number)
    namespace = metadata.get("namespace") or "default"
    name = metadata.get("name") or "pod-%d" % number
    pod_sc = as_dict(spec.get("securityContext"), "pod %s securityContext" % name)

    findings = []
    if spec.get("hostNetwork") is True:
        findings.append(("-", "hostNetwork"))
    for volume in as_list(spec.get("volumes"), "pod %s volumes" % name):
        if isinstance(volume, dict) and "hostPath" in volume:
            findings.append(("-", "hostPath %s" % (volume.get("name") or "?")))

    containers = spec.get("containers")
    if not isinstance(containers, list) or not containers:
        raise AuditError("pod %s has no containers list" % name)
    every = list(containers) + as_list(spec.get("initContainers"),
                                       "pod %s initContainers" % name)
    for index, container in enumerate(every, 1):
        if not isinstance(container, dict):
            raise AuditError("pod %s container %d is not an object" % (name, index))
        cname = container.get("name") or "container-%d" % index
        sc = as_dict(container.get("securityContext"),
                     "pod %s container %s securityContext" % (name, cname))
        resources = as_dict(container.get("resources"),
                            "pod %s container %s resources" % (name, cname))
        if sc.get("privileged") is True:
            findings.append((cname, "privileged"))
        if effective(sc, pod_sc, "runAsUser") == 0:
            findings.append((cname, "runAsRoot"))
        if effective(sc, pod_sc, "runAsNonRoot") is not True:
            findings.append((cname, "runAsNonRoot"))
        limits = resources.get("limits")
        if not isinstance(limits, dict) or not limits:
            findings.append((cname, "no limits"))
    return namespace, name, findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit pod securityContext, hostPath, hostNetwork and "
                    "resource limits in a kubectl JSON dump.",
        epilog="Exit codes: 0 clean, 1 findings, 2 usage or input error.")
    parser.add_argument("pods", nargs="?", default="-",
                        help="kubectl get pods -A -o json output, or - for stdin")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args(argv)

    try:
        items = pod_items(read_json(args.pods))
        total = 0
        findings = 0
        for number, pod in enumerate(items, 1):
            namespace, name, pod_findings = check_pod(pod, number)
            total += 1
            findings += len(pod_findings)
            if pod_findings and not args.quiet:
                for container, finding in pod_findings:
                    print("FAIL %s/%s %s %s" % (namespace, name, container, finding))
    except AuditError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if findings:
        print("ALERT %d finding%s in %d pod%s" % (
            findings, "" if findings == 1 else "s",
            total, "" if total == 1 else "s"))
        return 1
    print("OK no findings in %d pod%s" % (total, "" if total == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
