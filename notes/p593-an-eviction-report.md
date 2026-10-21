---
id: p593
title: "An eviction report"
slug: an-eviction-report
sections: [devsecops]
topic: "Python scripts"
tags: [Kubernetes, SRE, Python, CloudNative, Troubleshooting]
source: "LinkedIn post P593 · PythonFixes series"
linkedin_date: 2030-07-11
design: code
script: k8s_evictions.py
---

# An eviction report

At 03:10 six pods on one node are Evicted. The app team sees restarts; the node knows better.

## Quick reference

The full script is at the end of this note: `k8s_evictions.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 k8s_evictions.py /tmp/events.json
```

**Example output**

```text
EVICTED ip-10-0-12-44 memory 8
ALERT 15 evictions
```

## Explained

### What it does

The script reads the output of kubectl get events -A -o json. It keeps reason Evicted, takes the node from source.host and classifies the message as memory, disk, pid or other. It groups the count by node and reason, ranks the nodes and exits 1.

### What the screen shows

The 14 visible lines build a counter, skip every non-Evicted event, read the resource after 'resource: ' and reduce ephemeral-storage to disk. On the fixture they print EVICTED ip-10-0-12-44 memory 8, then ALERT 15 evictions.

### How to run it

`python3 k8s_evictions.py /tmp/events.json`, or pipe kubectl get events -A -o json into it. Exit 0 is clean, 1 is any eviction, 2 is bad input.

### The fix

For memory, right-size the requests and limits and check for a leak; then reserve enough for the kubelet. For disk, set ephemeral-storage limits, prune images and check the kubelet eviction threshold. For pid, find the fork leak before adding processes.

### Prevention

Run it daily and keep the report. A node that evicts twice in a week is undersized, not unlucky.

> **The honest caveat:** events expire after an hour by default, so a dump from yesterday proves nothing about last night. Collect them on a schedule or send them to a log store.

> **The lesson:** the node ran out before the pod did.

## In one line

> **The node ran out before the pod did.** Evictions are a capacity signal, not a pod bug.

**Rank the nodes**

```bash
python3 k8s_evictions.py /tmp/events.json
```

## Script: k8s_evictions.py

Download: [scripts/k8s_evictions.py](../scripts/k8s_evictions.py)

```python
#!/usr/bin/env python3
"""Rank pod evictions by node and by the resource that ran out.

Reads one read-only events export:

    kubectl get events -A -o json > /tmp/events.json
    python3 k8s_evictions.py /tmp/events.json

Every event with reason Evicted is grouped by the node that evicted the
pod and by the resource named in the message:

    memory     the node was low on memory (the usual 3 a.m. page)
    disk       ephemeral-storage, nodefs or imagefs was low
    pid        the node ran out of process IDs
    other      an eviction whose message names none of the above

Nodes are ranked by total evictions, then by reason. A node that evicts
three workloads in a week is not unlucky; it is undersized or leaking.

Usage:
    python3 k8s_evictions.py
    python3 k8s_evictions.py /tmp/events.json
    kubectl get events -A -o json | python3 k8s_evictions.py -
    python3 k8s_evictions.py /tmp/events.json --verbose

Exit codes: 0 no evictions, 1 at least one eviction, 2 usage, unreadable
or invalid input.

CI (fail a weekly capacity review):
    kubectl get events -A -o json > /tmp/events.json
    python3 k8s_evictions.py /tmp/events.json || exit 1

Cron (daily at 07:10, after the night batch):
    10 7 * * * kubectl get events -A -o json | python3 /opt/s0sta/k8s_evictions.py -

Read-only: it reads one local file or stdin and never calls the API
server. The node name comes from event.source.host, which the kubelet
sets on eviction events; an event without it is counted under unknown
rather than guessed. Evictions are only a symptom: check the node's
MemoryPressure or DiskPressure condition and its allocatable headroom.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys
from collections import Counter, defaultdict


class EvictionError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source):
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise EvictionError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise EvictionError("%s is not JSON: %s" % (source, exc))


def as_dict(value, label):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise EvictionError("%s must be an object" % label)
    return value


def as_list(value, label):
    if value is None:
        return []
    if not isinstance(value, list):
        raise EvictionError("%s must be a list" % label)
    return value


def items_of(doc, label):
    if not isinstance(doc, dict):
        raise EvictionError("%s must be a JSON object" % label)
    items = doc.get("items")
    if items is not None:
        return as_list(items, "%s items" % label)
    if "metadata" in doc or "kind" in doc:
        return [doc]
    raise EvictionError("%s has no items list and no metadata" % label)


def classify(message):
    text = message.lower()
    if "memory" in text or "oom" in text:
        return "memory"
    if ("storage" in text or "disk" in text or "nodefs" in text
            or "imagefs" in text):
        return "disk"
    if "pid" in text:
        return "pid"
    return "other"


def parse_event(event, number):
    """Return (node, reason, namespace, pod) for an Evicted event."""
    if not isinstance(event, dict):
        raise EvictionError("event %d is not an object" % number)
    if event.get("reason") != "Evicted":
        return None
    source = as_dict(event.get("source"), "event %d source" % number)
    node = source.get("host") or "unknown"
    if not isinstance(node, str):
        raise EvictionError("event %d source.host must be a string" % number)
    message = event.get("message") or ""
    if not isinstance(message, str):
        raise EvictionError("event %d message must be a string" % number)
    involved = as_dict(event.get("involvedObject"),
                       "event %d involvedObject" % number)
    pod = involved.get("name") or "?"
    namespace = involved.get("namespace") or "default"
    return node, classify(message), str(namespace), str(pod)


def plural(count, one, many):
    return one if count == 1 else many


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rank pod evictions by node and by memory, disk or pid.",
        epilog="Exit codes: 0 no evictions, 1 evictions found, 2 usage or "
               "input error.")
    parser.add_argument("events", nargs="?", default="-",
                        help="kubectl get events -A -o json output, or - for stdin")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="list the evicted pods under each row")
    args = parser.parse_args(argv)

    try:
        events = items_of(read_json(args.events), "event dump")
        totals = Counter()
        pods = defaultdict(list)
        for number, event in enumerate(events, 1):
            parsed = parse_event(event, number)
            if parsed is None:
                continue
            node, reason, namespace, pod = parsed
            totals[(node, reason)] += 1
            pods[(node, reason)].append("%s/%s" % (namespace, pod))
    except EvictionError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not totals:
        print("OK no evictions in %d %s" % (
            len(events), "event" if len(events) == 1 else "events"))
        return 0

    per_node = Counter()
    for (node, _reason), count in totals.items():
        per_node[node] += count
    ordered = sorted(totals.items(),
                     key=lambda item: (-per_node[item[0][0]], item[0][0],
                                       -item[1], item[0][1]))
    for (node, reason), count in ordered:
        print("EVICTED %s %s %d" % (node, reason, count))
        if args.verbose:
            for pod in sorted(pods[(node, reason)]):
                print("  %s" % pod)

    total = sum(totals.values())
    print("ALERT %d %s on %d %s" % (
        total, plural(total, "eviction", "evictions"),
        len(per_node), plural(len(per_node), "node", "nodes")))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
