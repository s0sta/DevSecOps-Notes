#!/usr/bin/env python3
"""Explain why pods are Pending from a kubectl JSON dump and its events.

Reads two read-only exports:

    kubectl get pods -A -o json > /tmp/pods.json
    kubectl get events -A -o json > /tmp/events.json

For every pod whose status.phase is Pending it finds the FailedScheduling
event and reports one short reason:

    cpu        the scheduler reports insufficient CPU
    memory     the scheduler reports insufficient memory
    taint      a node taint is not tolerated by the pod
    pvc        a PersistentVolumeClaim is unbound or missing
    affinity   node affinity, pod affinity or a node selector excludes nodes
    unknown    a scheduling event exists but names none of the above
    no event   no FailedScheduling event in the dump (a brand-new pod, or
               one blocked before the scheduler, such as a quota or an
               admission webhook)

Usage:
    python3 k8s_pending.py
    python3 k8s_pending.py /tmp/pods.json /tmp/events.json
    kubectl get pods -A -o json | python3 k8s_pending.py - /tmp/events.json
    python3 k8s_pending.py /tmp/pods.json /tmp/events.json --verbose

Exit codes: 0 no Pending pods, 1 at least one Pending pod, 2 usage,
unreadable or invalid input.

CI (fail the pipeline while anything is stuck):
    kubectl get pods -A -o json > /tmp/pods.json
    kubectl get events -A -o json > /tmp/events.json
    python3 k8s_pending.py /tmp/pods.json /tmp/events.json || exit 1

Cron (every five minutes, page on a new stuck pod):
    */5 * * * * kubectl get events -A -o json > /tmp/events.json && kubectl get pods -A -o json | python3 /opt/s0sta/k8s_pending.py - /tmp/events.json

Read-only: it parses two local files (or stdin) and never calls the API
server, so it is safe against production. The reason is only as good as
the event dump: a Pending pod can be blocked by a quota or a webhook that
never writes FailedScheduling, and an old event can describe a condition
that has since changed. Pair the output with kubectl describe pod.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys

CPU = ("insufficient cpu",)
MEMORY = ("insufficient memory",)
TAINT = ("taint", "untolerated taint")
PVC = ("persistentvolumeclaim", "unbound", "volume", "pvc")
AFFINITY = ("affinity", "selector", "didn't match", "did not match")


class PendingError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source):
    """Read one JSON document from a path or '-' for stdin."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise PendingError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise PendingError("%s is not JSON: %s" % (source, exc))


def as_dict(value, label):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PendingError("%s must be an object" % label)
    return value


def as_list(value, label):
    if value is None:
        return []
    if not isinstance(value, list):
        raise PendingError("%s must be a list" % label)
    return value


def items_of(doc, label):
    """Return the item list from a List, or wrap a single object."""
    if not isinstance(doc, dict):
        raise PendingError("%s must be a JSON object" % label)
    items = doc.get("items")
    if items is not None:
        return as_list(items, "%s items" % label)
    if "metadata" in doc or "kind" in doc:
        return [doc]
    raise PendingError("%s has no items list and no metadata" % label)


def kind_of(obj):
    return str(obj.get("kind") or "").lower()


def pod_identity(pod, number):
    metadata = as_dict(pod.get("metadata"), "pod %d metadata" % number)
    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        raise PendingError("pod %d has no metadata.name" % number)
    namespace = metadata.get("namespace") or "default"
    if not isinstance(namespace, str):
        raise PendingError("pod %d has a non-string namespace" % number)
    uid = metadata.get("uid")
    return namespace, name, uid if isinstance(uid, str) else ""


def pod_phase(pod, number):
    status = as_dict(pod.get("status"), "pod %d status" % number)
    phase = status.get("phase") or ""
    if not isinstance(phase, str):
        raise PendingError("pod %d status.phase must be a string" % number)
    return phase


def event_pod(event, number):
    """Return (namespace, name, uid, reason, message) for one event."""
    if not isinstance(event, dict):
        raise PendingError("event %d is not an object" % number)
    involved = as_dict(event.get("involvedObject"),
                       "event %d involvedObject" % number)
    if kind_of(involved) not in ("", "pod"):
        return None
    name = involved.get("name")
    if not isinstance(name, str) or not name:
        return None
    namespace = involved.get("namespace") or "default"
    uid = involved.get("uid") if isinstance(involved.get("uid"), str) else ""
    reason = event.get("reason") or ""
    message = event.get("message") or event.get("note") or ""
    if not isinstance(reason, str) or not isinstance(message, str):
        raise PendingError("event %d reason/message must be strings" % number)
    return namespace, name, uid, reason, message


def same_pod(event, namespace, name, uid):
    e_ns, e_name, e_uid, _reason, _message = event
    if e_ns != namespace or e_name != name:
        return False
    if uid and e_uid:
        return uid == e_uid
    return True


def classify(message):
    """Map one scheduler message to a short reason label."""
    text = message.lower()
    if any(token in text for token in CPU):
        return "cpu"
    if any(token in text for token in MEMORY):
        return "memory"
    if any(token in text for token in TAINT):
        return "taint"
    if any(token in text for token in PVC):
        return "pvc"
    if any(token in text for token in AFFINITY):
        return "affinity"
    return "unknown"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Explain Pending pods from kubectl pods and events JSON.",
        epilog="Exit codes: 0 no Pending pods, 1 Pending found, 2 usage or "
               "input error.")
    parser.add_argument("pods", nargs="?", default="-",
                        help="kubectl get pods -A -o json output, or - for stdin")
    parser.add_argument("events", nargs="?", default=None,
                        help="kubectl get events -A -o json output (optional)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the scheduler message for each pod")
    args = parser.parse_args(argv)

    try:
        pods = items_of(read_json(args.pods), "pod dump")
        events = []
        if args.events:
            events = items_of(read_json(args.events), "event dump")
        parsed_events = [event_pod(e, i) for i, e in enumerate(events, 1)]
        parsed_events = [e for e in parsed_events if e is not None]
        parsed_events = [e for e in parsed_events if e[3] == "FailedScheduling"]

        pending = []
        for number, pod in enumerate(pods, 1):
            if not isinstance(pod, dict):
                raise PendingError("pod %d is not an object" % number)
            if pod_phase(pod, number) != "Pending":
                continue
            namespace, name, uid = pod_identity(pod, number)
            messages = [e[4] for e in parsed_events
                        if same_pod(e, namespace, name, uid)]
            reason = "no event"
            detail = ""
            if messages:
                labels = [classify(m) for m in messages]
                reason = next((r for r in labels if r != "unknown"), "unknown")
                detail = next((m for m, r in zip(messages, labels)
                               if r == reason), messages[0])
            pending.append((namespace, name, reason, detail))
    except PendingError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not pending:
        print("OK %d pods scheduled" % len(pods))
        return 0

    for namespace, name, reason, detail in pending:
        print("PENDING %s/%s %s" % (namespace, name, reason))
        if args.verbose and detail:
            print("  %s" % detail)

    print("ALERT %d pending" % len(pending))
    if args.events is None:
        print("NOTE no events dump; reasons are unknown", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
