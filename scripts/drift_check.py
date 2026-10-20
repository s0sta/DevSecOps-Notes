#!/usr/bin/env python3
"""drift_check.py - find what changed in the cluster behind Git's back.

Walks a folder of Kubernetes manifests and runs `kubectl diff` against each
one. A manifest that no longer matches the live cluster is drift. Exit code
is 1 when drift (or a kubectl error) is found, so it drops into cron or a CI
step. Standard library only; needs kubectl on PATH and rights for a
server-side dry run.

Usage:
    python3 drift_check.py                     # scans ./deploy
    python3 drift_check.py path/to/manifests   # scans another folder
    python3 drift_check.py -n shop deploy      # fixed namespace
    python3 drift_check.py -q                  # only the summary

Cron (nightly at 02:00):
    0 2 * * * cd /srv/gitops && python3 drift_check.py -q >> /var/log/drift.log 2>&1

By s0sta.com
"""
import argparse
import subprocess
import sys
from pathlib import Path

SUFFIXES = (".yaml", ".yml")


def kubectl_diff(path, namespace=None, timeout=60):
    """Return (drifted, detail). detail is the diff or the error text."""
    cmd = ["kubectl", "diff", "-f", str(path)]
    if namespace:
        cmd += ["-n", namespace]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        sys.exit("kubectl not found on PATH")
    except subprocess.TimeoutExpired:
        return True, "timeout after %ss" % timeout
    if r.returncode == 0:
        return False, ""
    # kubectl diff: 0 = same, 1 = differences, >1 = error
    text = (r.stdout or "") + (r.stderr or "")
    return True, text.strip()


def main():
    ap = argparse.ArgumentParser(description="Detect drift between manifests and the live cluster.")
    ap.add_argument("root", nargs="?", default="deploy", help="folder of manifests, default deploy")
    ap.add_argument("-n", "--namespace", help="namespace for every file")
    ap.add_argument("-q", "--quiet", action="store_true", help="summary only")
    ap.add_argument("--timeout", type=int, default=60, help="seconds per file, default 60")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        sys.exit("not found: %s" % root)
    files = sorted(p for p in root.rglob("*") if p.suffix in SUFFIXES and p.is_file())
    if not files:
        sys.exit("no manifests under %s" % root)

    drifted, clean = [], 0
    for f in files:
        bad, detail = kubectl_diff(f, args.namespace, args.timeout)
        if bad:
            drifted.append(f)
            if not args.quiet:
                print("[DRIFT] %s" % f)
                for line in detail.splitlines()[:12]:
                    print("        " + line)
                if len(detail.splitlines()) > 12:
                    print("        ...")
        else:
            clean += 1

    print()
    print("checked %d, clean %d, drifted %d" % (len(files), clean, len(drifted)))
    if drifted:
        print("ALERT " + ", ".join(str(p) for p in drifted))
        sys.exit(1)
    print("OK no drift")
    sys.exit(0)


if __name__ == "__main__":
    main()
