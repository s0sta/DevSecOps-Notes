#!/usr/bin/env python3
"""Group image pull failures by image and by the reason in the event.

Reads one read-only events export:

    kubectl get events -A -o json > /tmp/events.json
    python3 image_pull_errors.py /tmp/events.json

It keeps events with reason Failed, ErrImagePull or ImagePullBackOff,
pulls the image name out of the message and classifies the cause. A
Failed event is kept only when its message mentions pull or image, so a
FailedMount or FailedCreate is not counted as a registry problem:

    auth       unauthorized, pull access denied, no basic auth credentials
    notfound   manifest unknown, repository or image does not exist
    timeout    i/o timeout, TLS handshake, connection refused, no such host
    other      a pull failure whose message fits none of the above

Images are counted per reason. The summary also counts registries other
than Docker Hub, because that is where a missing imagePullSecret usually
hides.

Usage:
    python3 image_pull_errors.py
    python3 image_pull_errors.py /tmp/events.json
    kubectl get events -A -o json | python3 image_pull_errors.py -
    python3 image_pull_errors.py /tmp/events.json --verbose

Exit codes: 0 no pull failures, 1 at least one failure, 2 usage,
unreadable or invalid input.

CI (fail the deploy check when an image cannot be pulled):
    kubectl get events -A -o json > /tmp/events.json
    python3 image_pull_errors.py /tmp/events.json || exit 1

Cron (daily at 07:20, after the night rollout):
    20 7 * * * kubectl get events -A -o json | python3 /opt/s0sta/image_pull_errors.py -

Read-only: it reads one local file or stdin and never calls the API
server. An event is evidence, not proof: the registry may have recovered,
and a transient timeout can appear once and never again. Check the pod's
imagePullSecrets and the registry status before changing a manifest.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import re
import sys
from collections import Counter


class PullError(Exception):
    """Anything that should end the run with exit code 2."""


REASONS = ("Failed", "ErrImagePull", "ImagePullBackOff")
AUTH = ("unauthorized", "authentication required", "no basic auth",
        "pull access denied", "access denied", "denied:", "forbidden")
NOTFOUND = ("not found", "manifest unknown", "does not exist",
            "no such image", "repository does not exist", "name unknown",
            "invalid reference")
TIMEOUT = ("timeout", "timed out", "connection refused", "no such host",
           "network is unreachable", "tls handshake", "i/o timeout",
           "context deadline exceeded", "dial tcp")
PUBLIC = ("docker.io", "index.docker.io", "registry-1.docker.io")
IMAGE_RE = re.compile(r'image "([^"]+)"')


def read_json(source):
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise PullError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise PullError("%s is not JSON: %s" % (source, exc))


def as_dict(value, label):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PullError("%s must be an object" % label)
    return value


def as_list(value, label):
    if value is None:
        return []
    if not isinstance(value, list):
        raise PullError("%s must be a list" % label)
    return value


def items_of(doc, label):
    if not isinstance(doc, dict):
        raise PullError("%s must be a JSON object" % label)
    items = doc.get("items")
    if items is not None:
        return as_list(items, "%s items" % label)
    if "metadata" in doc or "kind" in doc:
        return [doc]
    raise PullError("%s has no items list and no metadata" % label)


def classify(message):
    text = message.lower()
    if any(token in text for token in AUTH):
        return "auth"
    if any(token in text for token in NOTFOUND):
        return "notfound"
    if any(token in text for token in TIMEOUT):
        return "timeout"
    return "other"


def image_of(message):
    match = IMAGE_RE.search(message)
    if match:
        return match.group(1)
    return "?"


def registry_of(image):
    """Return the registry host, or docker.io for a short Docker Hub name."""
    if "/" not in image:
        return "docker.io"
    first = image.split("/", 1)[0]
    if "." in first or ":" in first or first == "localhost":
        return first
    return "docker.io"


def parse_event(event, number):
    if not isinstance(event, dict):
        raise PullError("event %d is not an object" % number)
    if event.get("reason") not in REASONS:
        return None
    message = event.get("message") or ""
    if not isinstance(message, str):
        raise PullError("event %d message must be a string" % number)
    text = message.lower()
    if event.get("reason") == "Failed" and "pull" not in text \
            and "image" not in text:
        return None
    return image_of(message), classify(message)


def plural(count, one, many):
    return one if count == 1 else many


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Group image pull failures by image, cause and registry.",
        epilog="Exit codes: 0 no failures, 1 failures found, 2 usage or "
               "input error.")
    parser.add_argument("events", nargs="?", default="-",
                        help="kubectl get events -A -o json output, or - for stdin")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print one line per registry as well")
    args = parser.parse_args(argv)

    try:
        events = items_of(read_json(args.events), "event dump")
        counts = Counter()
        for number, event in enumerate(events, 1):
            parsed = parse_event(event, number)
            if parsed is None:
                continue
            counts[parsed] += 1
    except PullError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not counts:
        print("OK no image pull failures in %d %s" % (
            len(events), "event" if len(events) == 1 else "events"))
        return 0

    registries = Counter()
    for (image, _reason), count in counts.items():
        if image != "?":
            registries[registry_of(image)] += count
    external = {name: count for name, count in registries.items()
                if name not in PUBLIC}

    for (image, reason), count in sorted(
            counts.items(), key=lambda item: (-item[1], item[0][0],
                                              item[0][1])):
        print("PULL %s %s %d" % (image, reason, count))
        if args.verbose:
            print("  registry %s" % registry_of(image))
    if args.verbose:
        for name, count in sorted(external.items(),
                                  key=lambda item: (-item[1], item[0])):
            print("EXTERNAL %s %d" % (name, count))

    total = sum(counts.values())
    summary = "ALERT %d failed %s" % (total, plural(total, "pull", "pulls"))
    if external:
        summary += ", %d external %s" % (
            len(external), plural(len(external), "registry", "registries"))
    print(summary)
    return 1


if __name__ == "__main__":
    sys.exit(main())
