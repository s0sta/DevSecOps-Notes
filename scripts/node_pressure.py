#!/usr/bin/env python3
"""Report node pressure conditions and allocatable headroom from nodes JSON.

Reads one read-only nodes export:

    kubectl get nodes -o json > /tmp/nodes.json
    python3 node_pressure.py /tmp/nodes.json

For every node it reads status.conditions and flags:

    MemoryPressure   the kubelet is evicting pods to reclaim memory
    DiskPressure     ephemeral-storage or imagefs is low
    PIDPressure      the node is short of process IDs
    NotReady         the Ready condition is False or Unknown

For a flagged node it also prints allocatable against capacity for CPU
and memory. Allocatable is the pod-facing ceiling; the gap to capacity
is what the kubelet and the system daemons reserve.

Usage:
    python3 node_pressure.py
    python3 node_pressure.py /tmp/nodes.json
    kubectl get nodes -o json | python3 node_pressure.py -
    python3 node_pressure.py /tmp/nodes.json --all

Exit codes: 0 no node under pressure, 1 at least one node under
pressure, 2 usage, unreadable or invalid input.

CI (fail a cluster health check):
    kubectl get nodes -o json > /tmp/nodes.json
    python3 node_pressure.py /tmp/nodes.json || exit 1

Cron (every ten minutes, alert before the evictions start):
    */10 * * * * kubectl get nodes -o json | python3 /opt/s0sta/node_pressure.py -

Read-only: it reads one local file or stdin and never calls the API
server. Capacity and allocatable are static limits, not live usage: a
node can be 97% allocated and still have free memory, or look empty and
be one cache away from pressure. Use kubectl top node for utilisation.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys


class PressureError(Exception):
    """Anything that should end the run with exit code 2."""


CPU_SUFFIX = {"n": 1e-9, "u": 1e-6, "m": 1e-3}
MEM_SUFFIX = {
    "Ki": 1024, "Mi": 1024 ** 2, "Gi": 1024 ** 3, "Ti": 1024 ** 4,
    "Pi": 1024 ** 5, "K": 1000, "M": 1000 ** 2, "G": 1000 ** 3,
    "T": 1000 ** 4, "P": 1000 ** 5,
}


def read_json(source):
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise PressureError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise PressureError("%s is not JSON: %s" % (source, exc))


def as_dict(value, label):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PressureError("%s must be an object" % label)
    return value


def as_list(value, label):
    if value is None:
        return []
    if not isinstance(value, list):
        raise PressureError("%s must be a list" % label)
    return value


def items_of(doc, label):
    if not isinstance(doc, dict):
        raise PressureError("%s must be a JSON object" % label)
    items = doc.get("items")
    if items is not None:
        return as_list(items, "%s items" % label)
    if "metadata" in doc or "kind" in doc:
        return [doc]
    raise PressureError("%s has no items list and no metadata" % label)


def cpu_cores(text):
    """Parse a Kubernetes CPU quantity into cores, or None."""
    if not isinstance(text, str) or not text:
        return None
    for suffix, factor in CPU_SUFFIX.items():
        if text.endswith(suffix):
            try:
                return float(text[:-len(suffix)]) * factor
            except ValueError:
                return None
    try:
        return float(text)
    except ValueError:
        return None


def mem_bytes(text):
    """Parse a Kubernetes memory quantity into bytes, or None."""
    if not isinstance(text, str) or not text:
        return None
    for suffix in sorted(MEM_SUFFIX, key=len, reverse=True):
        if text.endswith(suffix):
            try:
                return float(text[:-len(suffix)]) * MEM_SUFFIX[suffix]
            except ValueError:
                return None
    try:
        return float(text)
    except ValueError:
        return None


def fmt_cpu(value):
    if value is None:
        return "n/a"
    if value >= 10:
        return "%g" % round(value, 1)
    return "%g" % round(value, 3)


def fmt_mem(value):
    if value is None:
        return "n/a"
    for suffix, size in (("Ti", 1024 ** 4), ("Gi", 1024 ** 3),
                         ("Mi", 1024 ** 2)):
        if value >= size:
            return "%g%s" % (round(value / size, 1), suffix)
    return "%dB" % (round(value),)


def ratio(alloc, capacity):
    if alloc is None or capacity is None or capacity <= 0:
        return ""
    return " (%d%%)" % round(100 * alloc / capacity)


def node_report(node, number, show_all):
    if not isinstance(node, dict):
        raise PressureError("node %d is not an object" % number)
    metadata = as_dict(node.get("metadata"), "node %d metadata" % number)
    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        raise PressureError("node %d has no metadata.name" % number)
    status = as_dict(node.get("status"), "node %s status" % name)
    conditions = as_list(status.get("conditions"), "node %s conditions" % name)
    state = {}
    for index, cond in enumerate(conditions, 1):
        if not isinstance(cond, dict):
            raise PressureError("node %s condition %d is not an object"
                                % (name, index))
        kind = cond.get("type")
        if not isinstance(kind, str):
            raise PressureError("node %s condition %d has no type"
                                % (name, index))
        state[kind] = str(cond.get("status") or "Unknown")

    reasons = [kind for kind in ("MemoryPressure", "DiskPressure", "PIDPressure")
               if state.get(kind) == "True"]
    ready = state.get("Ready")
    if ready != "True":
        reasons.append("NotReady")
    if not reasons and not show_all:
        return name, None

    capacity = as_dict(status.get("capacity"), "node %s capacity" % name)
    allocatable = as_dict(status.get("allocatable"),
                          "node %s allocatable" % name)
    cpu_cap = cpu_cores(capacity.get("cpu"))
    cpu_alloc = cpu_cores(allocatable.get("cpu"))
    mem_cap = mem_bytes(capacity.get("memory"))
    mem_alloc = mem_bytes(allocatable.get("memory"))
    headroom = "ready=%s cpu %s/%s%s mem %s/%s%s" % (
        ready or "Unknown",
        fmt_cpu(cpu_alloc), fmt_cpu(cpu_cap), ratio(cpu_alloc, cpu_cap),
        fmt_mem(mem_alloc), fmt_mem(mem_cap), ratio(mem_alloc, mem_cap))
    return name, (reasons, headroom)


def plural(count, one, many):
    return one if count == 1 else many


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report node pressure conditions and allocatable headroom.",
        epilog="Exit codes: 0 no pressure, 1 pressure found, 2 usage or "
               "input error.")
    parser.add_argument("nodes", nargs="?", default="-",
                        help="kubectl get nodes -o json output, or - for stdin")
    parser.add_argument("-a", "--all", action="store_true",
                        help="print every node, including the healthy ones")
    args = parser.parse_args(argv)

    try:
        nodes = items_of(read_json(args.nodes), "node dump")
        reports = [node_report(node, number, args.all)
                   for number, node in enumerate(nodes, 1)]
    except PressureError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    flagged = 0
    for name, report in reports:
        if report is None:
            continue
        reasons, headroom = report
        if reasons:
            flagged += 1
        print("NODE %s %s" % (name, ",".join(reasons) or "ok"))
        print("  %s" % headroom)

    if not flagged:
        print("OK %d %s, no pressure" % (
            len(nodes), plural(len(nodes), "node", "nodes")))
        return 0

    print("ALERT %d of %d %s under pressure" % (
        flagged, len(nodes), plural(len(nodes), "node", "nodes")))
    return 1


if __name__ == "__main__":
    sys.exit(main())
