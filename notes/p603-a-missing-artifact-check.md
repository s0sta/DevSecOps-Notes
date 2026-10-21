---
id: p603
title: "A missing artifact check"
slug: a-missing-artifact-check
sections: [devsecops]
topic: "Python scripts"
tags: [CICD, SupplyChain, DevOps, Python, Artifacts]
source: "LinkedIn post P603 · PythonFixes series"
linkedin_date: 2030-08-04
design: code
script: artifact_missing.py
---

# A missing artifact check

The upload step is skipped after a retry, the deploy finds a manifest and downloads nothing, and the job stays green for eleven days. Every step that could have caught it was skipped by a condition.

## Quick reference

The full script is at the end of this note: `artifact_missing.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 artifact_missing.py release.json /srv/releases/1.4.2
```

**Example output**

```text
FINDING 2 bad artifacts
ALERT b.bin, c.bin
```

## Explained

### What it does

`artifact_missing.py` reads a manifest of artifacts: path, size and sha256 for each file. A relative path is resolved against the manifest directory or the root you pass. It checks that each file exists, that the byte count matches and that the hash matches, then exits 1 with the bad names.

### What the screen shows

The fourteen lines load the list, take the root and walk each entry. A missing file is appended and skipped. The rest are read at once, then size and hash are checked in one condition. The last two lines print FINDING 2 bad artifacts, then ALERT b.bin, c.bin.

### How to run it

`python3 artifact_missing.py release.json /srv/releases/1.4.2`. Exit 0 means every artifact matches, 1 means one is missing or corrupt, 2 means the manifest is wrong.

### The fix

Re-upload the missing file and rebuild the corrupt one. Do not edit the manifest to match the disk, because the manifest is what should exist.

### Prevention

Generate the manifest from the artifacts at build time and make the deploy step require a clean result.

> **The honest caveat:** a matching hash proves the bytes match the manifest, not that the build is reproducible or signed. A manifest generated from the same corrupt file agrees with itself.

> **The lesson:** a release is a manifest plus the bytes it names.

## In one line

> **No file, no release.** A manifest is a promise; the hash is the proof.

**Check one file**

```bash
sha256sum -c SHA256SUMS
```

## Script: artifact_missing.py

Download: [scripts/artifact_missing.py](../scripts/artifact_missing.py)

```python
#!/usr/bin/env python3
"""Check every artifact in a release manifest: present, sized, hashed.

Reads a release manifest, resolves each artifact path, and checks the file
against the manifest before anybody deploys it:

    exists        a missing file is the first failure
    size          the byte count must match, so a truncated upload fails
    sha256        the digest must match, so a swapped or corrupt file fails

The manifest is JSON:

    {"artifacts": [
      {"path": "api-1.4.2.tar.gz", "size": 1048576,
       "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"},
      {"path": "sbom.cdx.json", "size": 4096,
       "sha256": "..."}]}

"files" is accepted as an alias for "artifacts". A relative path is resolved
against the manifest directory, or against the root argument when one is
given:

    python3 artifact_missing.py release.json
    python3 artifact_missing.py release.json /srv/releases/1.4.2

Usage:
    python3 artifact_missing.py release.json /srv/releases/1.4.2
    python3 artifact_missing.py release.json --help

Exit codes: 0 every artifact matches, 1 at least one is missing or corrupt,
2 usage, or a manifest that is missing, unreadable, invalid or empty.

CI (before the deploy step, fail the job when an artifact is bad):
    python3 artifact_missing.py release.json /srv/releases/1.4.2 || exit 1

Cron (verify the release bucket after a copy):
    30 3 * * * python3 /opt/s0sta/artifact_missing.py /srv/releases/current/release.json

The script is read-only. It reads the manifest and each artifact, hashes the
bytes and writes nothing. A matching hash proves the file matches the
manifest; it does not prove the build is reproducible, signed or safe. Pair
it with a signature check and keep the manifest beside the artifact.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import hashlib
import json
import os
import sys

CHUNK = 1024 * 1024
HEX = set("0123456789abcdef")


class ManifestError(Exception):
    """Anything that should end the run with exit code 2."""


def load_manifest(path):
    """Return (manifest_dir, artifact list) or raise ManifestError."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise ManifestError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise ManifestError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(doc, dict):
        raise ManifestError("the manifest must be a JSON object")
    items = doc.get("artifacts")
    if items is None:
        items = doc.get("files")
    if not isinstance(items, list) or not items:
        raise ManifestError("the manifest has no non-empty artifacts list")
    return os.path.dirname(os.path.abspath(path)), items


def artifact_fields(item, number):
    """Validate one artifact entry and return (path, size, sha256)."""
    if not isinstance(item, dict):
        raise ManifestError("artifact %d is not an object" % number)
    path = item.get("path")
    size = item.get("size")
    digest = item.get("sha256")
    if not isinstance(path, str) or not path:
        raise ManifestError("artifact %d has no path" % number)
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ManifestError("artifact %s has no non-negative size" % path)
    if not isinstance(digest, str) or len(digest) != 64 or any(
            char not in HEX for char in digest.lower()):
        raise ManifestError("artifact %s has no sha256 hex digest" % path)
    return path, size, digest.lower()


def sha256_file(path):
    """Return the hex sha256 of a file, streaming it in one MiB chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(CHUNK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def check_one(path, size, digest):
    """Return a FAIL reason string, or None when the artifact is good."""
    if not os.path.isfile(path):
        return "missing"
    try:
        actual_size = os.path.getsize(path)
        if actual_size != size:
            return "size expected %d got %d" % (size, actual_size)
        actual_digest = sha256_file(path)
    except OSError as exc:
        return "unreadable (%s)" % exc
    if actual_digest != digest:
        return "sha256 expected %s got %s" % (digest[:12], actual_digest[:12])
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify release artifacts against a JSON manifest of "
                    "path, size and sha256.",
        epilog="Exit codes: 0 all good, 1 missing or corrupt, 2 usage or input error.")
    parser.add_argument("manifest", help="release manifest JSON")
    parser.add_argument("root", nargs="?",
                        help="directory for relative paths (default: manifest directory)")
    args = parser.parse_args(argv)

    try:
        manifest_dir, items = load_manifest(args.manifest)
        root = os.path.abspath(args.root) if args.root else manifest_dir
        if not os.path.isdir(root):
            raise ManifestError("root is not a directory: %s" % root)
        bad = []
        for number, item in enumerate(items, 1):
            rel, size, digest = artifact_fields(item, number)
            path = rel if os.path.isabs(rel) else os.path.join(root, rel)
            reason = check_one(path, size, digest)
            if reason is not None:
                if rel not in bad:
                    bad.append(rel)
                print("FAIL %s %s" % (rel, reason))
    except ManifestError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if bad:
        shown = ", ".join(bad[:5])
        if len(bad) > 5:
            shown += " +%d more" % (len(bad) - 5)
        print("FINDING %d bad artifacts" % len(bad))
        print("ALERT %s" % shown)
        return 1
    print("OK %d artifacts match" % len(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
