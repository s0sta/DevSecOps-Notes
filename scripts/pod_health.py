#!/usr/bin/env python3
"""pod_health.py - a quick health summary of your Kubernetes pods.

Reads `kubectl get pods -o json` and prints only what is wrong: pods that are
not Running/Succeeded, containers that are not ready, and restart counts.
Turns a long pod list into a short problem list. Standard library only.

Usage:
    kubectl get pods -A -o json | python3 pod_health.py
    python3 pod_health.py pods.json          # from a saved file

Exit code is 1 if any pod is unhealthy, so it works in CI and alerts.

By s0sta.com
"""
import json
import sys


def load(args):
    if args and args[0] != "-":
        with open(args[0]) as fh:
            return json.load(fh)
    return json.load(sys.stdin)


def main():
    data = load(sys.argv[1:])
    items = data.get("items", [])
    unhealthy = []
    for pod in items:
        meta = pod.get("metadata", {})
        name = meta.get("name", "?")
        ns = meta.get("namespace", "default")
        status = pod.get("status", {})
        phase = status.get("phase", "Unknown")
        conts = status.get("containerStatuses", []) or []
        ready = sum(1 for c in conts if c.get("ready"))
        total = len(conts)
        restarts = sum(c.get("restartCount", 0) for c in conts)
        bad = phase not in ("Running", "Succeeded") or (total and ready < total) or restarts >= 5
        if bad:
            unhealthy.append((ns, name, phase, f"{ready}/{total}", restarts))

    print(f"{len(items)} pods checked, {len(unhealthy)} need attention\n")
    if unhealthy:
        print(f"{'NAMESPACE':<16}{'POD':<40}{'PHASE':<12}{'READY':<8}RESTARTS")
        for ns, name, phase, ready, restarts in unhealthy:
            print(f"{ns:<16}{name:<40}{phase:<12}{ready:<8}{restarts}")
    else:
        print("[OK] all pods healthy")
    sys.exit(1 if unhealthy else 0)


if __name__ == "__main__":
    main()
