#!/usr/bin/env python3
"""Check whether every Deployment has a usable rollback target.

Reads the output of `kubectl get deploy,rs -n prod -o json` and answers one
question per Deployment: if this release is bad, what does `kubectl rollout
undo` actually return to?

Three things must be true:

  * revisionHistoryLimit is greater than 0, so old ReplicaSets are kept
  * the Deployment records a revision (deployment.kubernetes.io/revision)
  * the ReplicaSet for the immediately previous revision still exists, is
    scaled to zero, and no older ReplicaSet is still running replicas

A Deployment with no annotation, revision 1, revisionHistoryLimit 0, a gap
at the previous revision, or a previous ReplicaSet with replicas has no clean
rollback target. A Deployment with a target prints its current and previous
revision.

Usage:
    kubectl get deploy,rs -n prod -o json > /tmp/deploy.json
    python3 rollback_ready.py /tmp/deploy.json
    kubectl get deploy,rs -n prod -o json | python3 rollback_ready.py -

Exit codes: 0 every Deployment is rollback ready, 1 at least one is not,
2 usage or unreadable, missing or invalid input.

CI (before the release step, fail when a Deployment cannot roll back):
    kubectl get deploy,rs -n prod -o json > /tmp/deploy.json
    python3 rollback_ready.py /tmp/deploy.json || exit 1

Cron (weekly policy check):
    0 6 * * 1 kubectl get deploy,rs -A -o json | python3 /opt/s0sta/rollback_ready.py -

The check is read-only: one file or stdin, no API calls, no writes. A target
ReplicaSet is necessary, not sufficient: the old image must still exist in
the registry, and a database migration may not be reversible. The check does
not prove that rollback restores service.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys

REVISION = "deployment.kubernetes.io/revision"


class RollbackError(Exception):
    """Anything that should end the run with exit code 2."""


def load_json(source):
    """Read the kubectl dump from a path, or stdin when source is '-'."""
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise RollbackError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise RollbackError("%s is not valid JSON: %s" % (source, exc))


def objects(doc):
    """Return a list of typed objects from a List or a split dump."""
    if isinstance(doc, list):
        return doc
    if not isinstance(doc, dict):
        raise RollbackError("the dump must be a JSON object or list")
    if isinstance(doc.get("items"), list):
        return doc["items"]
    if isinstance(doc.get("deployments"), list) or isinstance(doc.get("replicasets"), list):
        deployments = doc.get("deployments") or []
        replicasets = doc.get("replicasets") or []
        if not isinstance(deployments, list) or not isinstance(replicasets, list):
            raise RollbackError("deployments and replicasets must be lists")
        return deployments + replicasets
    if doc.get("kind") in ("Deployment", "ReplicaSet"):
        return [doc]
    raise RollbackError("no items, deployments or replicasets in the dump")


def metadata_of(obj, label):
    """Return metadata and annotations for one object."""
    metadata = obj.get("metadata")
    if not isinstance(metadata, dict):
        raise RollbackError("%s has no metadata object" % label)
    annotations = metadata.get("annotations")
    if annotations is None:
        annotations = {}
    if not isinstance(annotations, dict):
        raise RollbackError("%s annotations must be an object" % label)
    return metadata, annotations


def revision_of(annotations):
    """Return the integer revision annotation, or None when absent or bad."""
    value = annotations.get(REVISION)
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    if isinstance(value, str) and value.isdigit() and int(value) > 0:
        return int(value)
    return None


def owned_replicasets(deployment, replicasets):
    """Return (revision, replicas, name) for ReplicaSets owned by deployment."""
    metadata, _ = metadata_of(deployment, "Deployment")
    name = metadata.get("name")
    namespace = metadata.get("namespace") or "default"
    owned = []
    for index, replica in enumerate(replicasets, 1):
        if not isinstance(replica, dict):
            raise RollbackError("ReplicaSet %d is not an object" % index)
        meta, annotations = metadata_of(replica, "ReplicaSet %d" % index)
        owners = meta.get("ownerReferences")
        if owners is None:
            continue
        if not isinstance(owners, list):
            raise RollbackError("ReplicaSet %s ownerReferences must be a list" % meta.get("name"))
        match = any(
            isinstance(owner, dict)
            and owner.get("kind") == "Deployment"
            and owner.get("name") == name
            for owner in owners)
        if not match:
            continue
        if (meta.get("namespace") or "default") != namespace:
            continue
        spec = replica.get("spec")
        if not isinstance(spec, dict):
            raise RollbackError("ReplicaSet %s has no spec object" % meta.get("name"))
        replicas = spec.get("replicas", 1)
        if isinstance(replicas, bool) or not isinstance(replicas, int) or replicas < 0:
            raise RollbackError("ReplicaSet %s spec.replicas must be non-negative" % meta.get("name"))
        owned.append((revision_of(annotations),
                      replicas, meta.get("name") or "replicaset-%d" % index))
    return owned


def check_deployment(deployment, replicasets, number):
    """Return (name, reason or None, detail) for one Deployment."""
    metadata, annotations = metadata_of(deployment, "Deployment %d" % number)
    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        raise RollbackError("Deployment %d has no name" % number)
    spec = deployment.get("spec")
    if not isinstance(spec, dict):
        raise RollbackError("Deployment %s has no spec object" % name)
    limit = spec.get("revisionHistoryLimit", 10)
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
        raise RollbackError("Deployment %s revisionHistoryLimit must be non-negative" % name)
    current = revision_of(annotations)
    owned = owned_replicasets(deployment, replicasets)
    known = [(rev, replicas, rs_name) for rev, replicas, rs_name in owned if rev]

    if current is None:
        return name, "no revision annotation", "?"
    if limit == 0:
        return name, "revisionHistoryLimit 0", str(current)
    if current < 2:
        return name, "revision 1 is the first", str(current)
    if any(rev > current for rev, _, _ in known):
        return name, "ReplicaSet revision ahead of Deployment", str(current)
    running = [(rev, replicas, rs_name) for rev, replicas, rs_name in known
               if rev < current and replicas > 0]
    if running:
        rev, replicas, rs_name = sorted(running)[-1]
        return name, "old ReplicaSet %s has %d replicas" % (rs_name, replicas), str(current)
    previous = [(rev, replicas, rs_name) for rev, replicas, rs_name in known
                if rev == current - 1]
    if not previous:
        older = [rev for rev, _, _ in known if rev < current]
        if older:
            return name, "no ReplicaSet at revision %d" % (current - 1), str(current)
        return name, "no previous ReplicaSet", str(current)
    return name, None, str(current)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check Deployments for a rollback target: history limit, "
                    "previous ReplicaSet and current revision.",
        epilog="Exit codes: 0 rollback ready, 1 no target, 2 usage or input error.")
    parser.add_argument("dump", nargs="?", default="-",
                        help="kubectl get deploy,rs -o json output, or - for stdin")
    args = parser.parse_args(argv)

    try:
        items = objects(load_json(args.dump))
        deployments = [x for x in items if isinstance(x, dict)
                       and x.get("kind") == "Deployment"]
        replicasets = [x for x in items if isinstance(x, dict)
                       and x.get("kind") == "ReplicaSet"]
        if not deployments:
            raise RollbackError("the dump has no Deployment objects")
        results = [check_deployment(d, replicasets, i)
                   for i, d in enumerate(deployments, 1)]
    except RollbackError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    bad = []
    for name, reason, current in results:
        if reason is None:
            print("OK %s revision %s has a target" % (name, current))
        else:
            print("FAIL %s %s" % (name, reason))
            bad.append(name)
    if bad:
        print("FINDING %d no rollback" % len(bad))
        print("ALERT %s" % ", ".join(bad))
        return 1
    word = "deployment has" if len(results) == 1 else "deployments have"
    print("OK %d %s a rollback target" % (len(results), word))
    return 0


if __name__ == "__main__":
    sys.exit(main())
