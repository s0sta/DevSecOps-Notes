---
id: p436
title: "A flaky test detector in Python"
slug: a-flaky-test-detector-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Testing, CICD, Python, DevOps, FlakyTests]
source: "LinkedIn post P436 · DevOps series"
linkedin_date: 2029-07-10
design: code
script: flaky_tests.py
---

# A flaky test detector in Python

A test that fails once a week is worse than a test that fails every time: it teaches the team to press re-run.

## Quick reference

The full script is at the end of this note: `flaky_tests.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 flaky_tests.py run-1.xml run-2.xml run-3.xml
```

**Example output**

```text
tests.test_api::test_timeout
tests.test_auth::test_expiry
```

## Explained

### What it does

`flaky_tests.py` reads two or more JUnit XML files, one per run. It walks every testcase, treats a failure or error child as failed, skipped as neither, and anything else as passed. Any test that both passed and failed across the runs is printed. Exit 1 means at least one flaky test, 0 means the runs agree, and 2 means a file is missing or is not JUnit XML.

### Why JUnit XML

JUnit XML is the format most runners can emit: pytest with `--junitxml`, gotestsum, jest-junit, and the GitLab and Jenkins parsers. A testcase carries classname and name, and a failure is a child element, not an attribute. Reading that shape means one script works across languages and CI vendors.

### How to use it

Run it over the last few exports: `python3 flaky_tests.py run-1.xml run-2.xml run-3.xml`. In CI, download the JUnit reports from the last ten runs and fail a nightly job when the list is non-empty. Then quarantine the test, fix it, or delete it. Retrying until green is the one answer that makes it worse.

> **The honest caveat:** two runs prove very little. A test that passes twice and fails once needs a third run, and a test that fails for an environmental reason looks exactly like a flaky one.

> **The lesson:** a flaky test is a measurement you cannot trust, and an untrusted suite stops being a gate.

## In one line

> **A rerun is not a fix.** Two runs disagree; one of them is wrong.

**Fail on flaky:** `flaky_tests.py run-*.xml`

## Script: flaky_tests.py

Download: [scripts/flaky_tests.py](../scripts/flaky_tests.py)

```python
#!/usr/bin/env python3
"""flaky_tests.py - find tests that both passed and failed across JUnit runs.

Reads two or more JUnit XML reports, one per run, and reports every test that
passed in at least one run and failed in at least one other. A testcase counts
as failed when it contains a <failure> or <error> child, as skipped when it
contains <skipped> and no failure, and as passed otherwise. A report may be a
single <testsuite> or a <testsuites> wrapper.

Usage:
    python3 flaky_tests.py run-1.xml run-2.xml
    python3 flaky_tests.py reports/*.xml
    python3 flaky_tests.py --quiet run-1.xml run-2.xml run-3.xml

CI (after downloading the JUnit reports of the last runs):
    python3 flaky_tests.py junit/*.xml || exit 1

Cron (a nightly flake report over the week's reports):
    0 3 * * * python3 /opt/scripts/flaky_tests.py /var/lib/junit/*.xml -q

Exit codes: 0 no flaky test, 1 at least one flaky test, 2 usage or input error.
Read-only: every file is opened for reading and nothing is written.

By s0sta.com
"""
import argparse
import sys
import xml.etree.ElementTree as ET

FAIL_TAGS = ("failure", "error")


def case_id(case, path):
    """Return classname::name for one testcase, or raise ValueError."""
    classname = (case.get("classname") or "").strip()
    name = (case.get("name") or "").strip()
    if not name:
        raise ValueError("%s: a testcase has no name attribute" % path)
    if classname:
        return "%s::%s" % (classname, name)
    return name


def case_state(case):
    """Return failed, skipped or passed for one testcase element."""
    tags = {child.tag for child in case}
    if tags.intersection(FAIL_TAGS):
        return "failed"
    if "skipped" in tags:
        return "skipped"
    return "passed"


def read_run(path):
    """Return {test id: state} for one JUnit report, or raise ValueError."""
    try:
        tree = ET.parse(path)
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc.strerror or exc))
    except ET.ParseError as exc:
        raise ValueError("%s is not well-formed XML: %s" % (path, exc))
    root = tree.getroot()
    if root.tag not in ("testsuite", "testsuites"):
        raise ValueError("%s: root element is <%s>, not <testsuite>"
                         % (path, root.tag))
    run = {}
    for case in root.iter("testcase"):
        key = case_id(case, path)
        state = case_state(case)
        if run.get(key) == "failed" or state == "failed":
            run[key] = "failed"
        elif run.get(key) == "passed" or state == "passed":
            run[key] = "passed"
        else:
            run.setdefault(key, state)
    if not run:
        raise ValueError("%s: no testcase elements" % path)
    return run


def main():
    parser = argparse.ArgumentParser(
        prog="flaky_tests.py",
        description="Find tests that both passed and failed across JUnit XML "
                    "runs.",
        epilog="Read-only. Exit 0 no flaky test, 1 flaky tests found, "
               "2 usage or input error.",
    )
    parser.add_argument("files", nargs="+", metavar="JUNIT.xml",
                        help="two or more JUnit XML reports, one per run")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args()

    if len(args.files) < 2:
        parser.error("give at least two JUnit XML files, one per run")

    runs, states, broken = [], {}, False
    for path in args.files:
        try:
            run = read_run(path)
        except ValueError as exc:
            print("error: %s" % exc, file=sys.stderr)
            broken = True
            continue
        runs.append((path, run))
        for key, state in run.items():
            states.setdefault(key, set()).add(state)

    if len(runs) < 2:
        print("error: need at least two valid JUnit reports, got %d"
              % len(runs), file=sys.stderr)
        return 2

    flaky = sorted(key for key, seen in states.items()
                   if "passed" in seen and "failed" in seen)

    if not args.quiet:
        for path, run in runs:
            failed = sum(1 for state in run.values() if state == "failed")
            skipped = sum(1 for state in run.values() if state == "skipped")
            print("%s: %d test%s, %d failed, %d skipped"
                  % (path, len(run), "" if len(run) == 1 else "s",
                     failed, skipped))
        for key in flaky:
            passed = sum(1 for _p, run in runs if run.get(key) == "passed")
            failed = sum(1 for _p, run in runs if run.get(key) == "failed")
            print("  %s  passed %d, failed %d" % (key, passed, failed))

    print("%d flaky test%s in %d run%s"
          % (len(flaky), "" if len(flaky) == 1 else "s",
             len(runs), "" if len(runs) == 1 else "s"))
    if broken:
        return 2
    return 1 if flaky else 0


if __name__ == "__main__":
    sys.exit(main())
```
