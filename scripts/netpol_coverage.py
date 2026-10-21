#!/usr/bin/env python3
"""Report NetworkPolicy coverage for every pod in a cluster dump.

Reads two JSON documents:

    kubectl get pods -A -o json          the pods
    kubectl get networkpolicy -A -o json the policies

and reports two gaps:

    NOPOLICY    a namespace with pods but no NetworkPolicy at all
    UNSELECTED  a pod that no NetworkPolicy in its namespace selects

Pods in a namespace with no policy at all are covered by the NOPOLICY line
and are not listed again as UNSELECTED. A policy that selects no pods still
lets the namespace pass the first check; its pods then fail the second.

A policy selects a pod when its spec.podSelector matches the pod labels in
the same namespace. An empty selector selects every pod in that namespace.
matchLabels and all four matchExpressions operators are supported: In, NotIn,
Exists and DoesNotExist.

Usage:
    kubectl get pods -A -o json > /tmp/pods.json
    kubectl get networkpolicy -A -o json > /tmp/netpols.json
    python3 netpol_coverage.py /tmp/pods.json /tmp/netpols.json
    python3 netpol_coverage.py /tmp/pods.json /tmp/netpols.json --quiet

Exit codes: 0 every pod is selected, 1 at least one gap, 2 usage,
unreadable or invalid input.

CI (fail the job on an uncovered namespace or pod):
    python3 netpol_coverage.py /tmp/pods.json /tmp/netpols.json || exit 1
Cron (daily at 07:00):
    0 7 * * * python3 /opt/s0sta/netpol_coverage.py /srv/k8s/pods.json /srv/k8s/netpols.json

Coverage is not correctness: a policy can select a pod and still allow the
wrong traffic, a policy with only egress rules leaves ingress open, and the
CNI must actually enforce NetworkPolicy. This report finds pods with no
policy in front of them, not pods with a bad policy.

Read-only: opens two local files and writes nothing.
Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys


class CoverageError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source, label):
    """Read one JSON document from a file or '-' for stdin."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise CoverageError("cannot read %s %s: %s" % (label, source, exc))
    except ValueError as exc:
        raise CoverageError("%s %s is not JSON: %s" % (label, source, exc))


def items_of(doc, label):
    """Return the item list from a List, a single object, or an items wrapper."""
    if not isinstance(doc, dict):
        raise CoverageError("%s must be a JSON object" % label)
    items = doc.get("items")
    if items is not None:
        if not isinstance(items, list):
            raise CoverageError("%s items must be a list" % label)
        return items
    if "metadata" in doc and "spec" in doc:
        return [doc]
    raise CoverageError("%s has no items list" % label)


def as_dict(value, label):
    """Return a mapping, or raise when the field has the wrong shape."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise CoverageError("%s must be an object" % label)
    return value


def match_selector(selector, labels, where):
    """Return True when a NetworkPolicy podSelector matches these labels."""
    if selector is None:
        raise CoverageError("%s has no podSelector" % where)
    if not isinstance(selector, dict):
        raise CoverageError("%s podSelector must be an object" % where)

    match_labels = selector.get("matchLabels")
    if match_labels is not None:
        if not isinstance(match_labels, dict):
            raise CoverageError("%s matchLabels must be an object" % where)
        for key, value in match_labels.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise CoverageError("%s matchLabels must map strings to strings" % where)
            if labels.get(key) != value:
                return False

    expressions = selector.get("matchExpressions")
    if expressions is not None:
        if not isinstance(expressions, list):
            raise CoverageError("%s matchExpressions must be a list" % where)
        for expression in expressions:
            if not isinstance(expression, dict):
                raise CoverageError("%s matchExpression must be an object" % where)
            key = expression.get("key")
            operator = expression.get("operator")
            values = expression.get("values", [])
            if not isinstance(key, str) or not isinstance(operator, str):
                raise CoverageError("%s matchExpression needs key and operator" % where)
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                raise CoverageError("%s matchExpression values must be a list of strings" % where)
            present = key in labels
            if operator == "In":
                if not values or labels.get(key) not in values:
                    return False
            elif operator == "NotIn":
                if not values:
                    raise CoverageError("%s NotIn needs at least one value" % where)
                if present and labels.get(key) in values:
                    return False
            elif operator == "Exists":
                if not present:
                    return False
            elif operator == "DoesNotExist":
                if present:
                    return False
            else:
                raise CoverageError("%s has unknown operator %s" % (where, operator))
    return True


def load_pods(doc):
    """Return [(namespace, name, labels)] and the namespace set."""
    pods = []
    namespaces = {}
    for number, pod in enumerate(items_of(doc, "pods"), 1):
        if not isinstance(pod, dict):
            raise CoverageError("pod %d is not an object" % number)
        metadata = as_dict(pod.get("metadata"), "pod %d metadata" % number)
        namespace = metadata.get("namespace") or "default"
        name = metadata.get("name") or "pod-%d" % number
        labels = as_dict(metadata.get("labels"), "pod %s labels" % name)
        if not all(isinstance(k, str) and isinstance(v, str)
                   for k, v in labels.items()):
            raise CoverageError("pod %s labels must map strings to strings" % name)
        pods.append((namespace, name, labels))
        namespaces[namespace] = namespaces.get(namespace, 0) + 1
    return pods, namespaces


def load_policies(doc):
    """Return {namespace: [(name, podSelector)]}."""
    policies = {}
    for number, policy in enumerate(items_of(doc, "networkpolicies"), 1):
        if not isinstance(policy, dict):
            raise CoverageError("policy %d is not an object" % number)
        metadata = as_dict(policy.get("metadata"), "policy %d metadata" % number)
        namespace = metadata.get("namespace") or "default"
        name = metadata.get("name") or "policy-%d" % number
        spec = as_dict(policy.get("spec"), "policy %s spec" % name)
        if "podSelector" not in spec:
            raise CoverageError("policy %s has no podSelector" % name)
        selector = spec.get("podSelector")
        if not isinstance(selector, dict):
            raise CoverageError("policy %s podSelector must be an object" % name)
        policies.setdefault(namespace, []).append((name, selector))
    return policies


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report namespaces without a NetworkPolicy and pods that no "
                    "NetworkPolicy selects.",
        epilog="Exit codes: 0 every pod is selected, 1 gaps found, 2 usage or input error.")
    parser.add_argument("pods", help="kubectl get pods -A -o json file, or - for stdin")
    parser.add_argument("policies", help="kubectl get networkpolicy -A -o json file, or - for stdin")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args(argv)

    if args.pods == "-" and args.policies == "-":
        parser.error("pods and policies cannot both read from stdin")

    try:
        pods, namespaces = load_pods(read_json(args.pods, "pods"))
        policies = load_policies(read_json(args.policies, "networkpolicies"))

        no_policy = sorted(ns for ns in namespaces if ns not in policies)
        unselected = []
        for namespace, name, labels in pods:
            if namespace in no_policy:
                continue
            selected = False
            for policy_name, selector in policies[namespace]:
                where = "policy %s/%s" % (namespace, policy_name)
                if match_selector(selector, labels, where):
                    selected = True
                    break
            if not selected:
                unselected.append((namespace, name))
    except CoverageError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not args.quiet:
        for namespace in no_policy:
            print("NOPOLICY %s" % namespace)
        for namespace, name in unselected:
            print("UNSELECTED %s/%s" % (namespace, name))

    gaps = len(no_policy) + len(unselected)
    if gaps:
        print("ALERT %d gap%s: %d namespace%s, %d pod%s" % (
            gaps, "" if gaps == 1 else "s",
            len(no_policy), "" if len(no_policy) == 1 else "s",
            len(unselected), "" if len(unselected) == 1 else "s"))
        return 1
    print("OK all pods selected: %d in %d namespace%s" % (
        len(pods), len(namespaces), "" if len(namespaces) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
