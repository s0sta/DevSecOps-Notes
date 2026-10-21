#!/usr/bin/env python3
"""docker_cis.py - check a Docker daemon info dump against five CIS settings.

Reads the JSON printed by `docker info --format '{{json .}}'` and checks five
daemon settings that the CIS Docker Benchmark calls out. Every setting is
reported as OK or WEAK, and the script exits 1 if any is weak.

    live      LiveRestoreEnabled is true          live restore
    proxy     UserlandProxy is false             userland proxy
    ulimit    DefaultUlimits is set              default ulimit
    logging   LoggingDriver is not json-file     centralised logging
    userns    SecurityOptions includes userns    user namespace support

The check names follow the CIS Docker Benchmark. Its section numbers move
between editions, so they are not quoted here.

Usage:
    docker info --format '{{json .}}' > /tmp/docker-info.json
    python3 docker_cis.py /tmp/docker-info.json
    docker info --format '{{json .}}' | python3 docker_cis.py -
    python3 docker_cis.py --help

CI (check the host before it joins the pool):
    python3 docker_cis.py /tmp/docker-info.json || exit 1

Cron (every Monday at 06:00):
    0 6 * * 1 docker info --format '{{json .}}' | python3 /opt/s0sta/docker_cis.py - >> /var/log/docker-cis.log

Exit codes: 0 all five settings are strong, 1 at least one is weak,
2 usage or unreadable/invalid input.

Read-only: the dump is read; the daemon is not contacted, reconfigured or
restarted. A missing key is treated as its default, which is weak here.

This is a configuration smoke test, not a full CIS benchmark. It does not
read daemon.json, file permissions, audit rules or kernel settings that the
benchmark also requires.

By s0sta.com
"""
import argparse
import json
import sys


def load(path):
    """Read one JSON document; raise ValueError on any input problem."""
    try:
        if path == "-":
            return json.load(sys.stdin)
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise ValueError("%s: %s" % (path, exc))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("%s: not valid JSON: %s" % (path, exc))


def checks(info):
    """Return (name, is_weak) for the five settings, in report order."""
    raw = info.get("SecurityOptions")
    if isinstance(raw, list):
        security = " ".join(str(item) for item in raw)
    else:
        security = str(raw or "")
    ulimits = info.get("DefaultUlimits") or []
    logging_driver = info.get("LoggingDriver") or "json-file"
    return [
        ("live", info.get("LiveRestoreEnabled") is not True),
        ("proxy", info.get("UserlandProxy") is not False),
        ("ulimit", not ulimits),
        ("logging", logging_driver == "json-file"),
        ("userns", "userns" not in security),
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check docker info JSON against five CIS-ish settings.")
    parser.add_argument("info", nargs="?", default="-",
                        help="docker info JSON file; stdin when omitted")
    args = parser.parse_args(argv)
    try:
        info = load(args.info)
        if not isinstance(info, dict):
            raise ValueError("%s: expected a JSON object" % args.info)
        results = checks(info)
    except ValueError as exc:
        print("docker_cis: %s" % exc, file=sys.stderr)
        return 2
    print(" ".join(name + ("=WEAK" if weak else "=OK")
                   for name, weak in results))
    weak = sum(1 for _, bad in results if bad)
    print("WEAK %d of %d" % (weak, len(results)))
    return 1 if weak else 0


if __name__ == "__main__":
    sys.exit(main())
