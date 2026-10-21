---
id: p606
title: "A pipeline flake report"
slug: a-pipeline-flake-report
sections: [devsecops]
topic: "Python scripts"
tags: [CICD, DevOps, Python, SRE, Automation]
source: "LinkedIn post P606 · PythonFixes series"
linkedin_date: 2030-08-11
design: code
script: pipeline_flake.py
---

# A pipeline flake report

The integration job fails twice a week, someone clicks rerun, and it goes green. By Friday the team calls it flaky with no number behind the word, so nobody knows whether it is getting worse or which job to fix first.

## Quick reference

The full script is at the end of this note: `pipeline_flake.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 pipeline_flake.py /tmp/runs.json
```

**Example output**

```text
FLAKY api-tests 40% failed
FLAKY e2e 30% failed
```

## Explained

### What it does

`pipeline_flake.py` reads CI history JSON with one record per job per run: id, job, status and duration. It counts passes and failures per job, keeps the jobs that have both, and ranks them by failures divided by the runs that reached a pass or fail. Only jobs above the threshold, 20 percent by default, are printed.

### What the screen shows

The fourteen lines load the runs and count each job into a two-item list. The bad list keeps jobs with both counts, filters at 20 percent and sorts. Two ranked lines are printed with the job and the rounded rate. On the dirty history they read FLAKY api-tests 40% failed, then FLAKY e2e 30% failed, and the script exits 1.

### How to run it

`python3 pipeline_flake.py runs.json`, with `--threshold 10` for a new job.

### The fix

Quarantine the top job or fix the failure behind it. A rerun that passes is evidence of a flake, not a fix.

### Prevention

Keep the weekly report and compare it with last week. A rate that doubles is a regression even below the threshold.

> **The honest caveat:** a history without reruns understates the rate, and duration is not used to rank.

> **The lesson:** measure instability before you schedule work around it.

## In one line

> **Flaky is a rate, not a feeling.** Count the reruns before you call a job unstable.

**Export the runs**

```bash
python3 pipeline_flake.py runs.json
```

## Script: pipeline_flake.py

Download: [scripts/pipeline_flake.py](../scripts/pipeline_flake.py)

```python
#!/usr/bin/env python3
"""Report CI jobs that both passed and failed, ranked by flake rate.

Reads a CI run history as JSON. Each record needs a job name and a status;
run id and duration may be present; they are not needed for the rate. A job is flaky when
the same job has at least one pass and at least one failure in the history.
Its flake rate is failures divided by the runs that reached a pass or fail:

    {"runs": [
      {"id": 101, "job": "api-tests", "status": "passed", "duration": 82},
      {"id": 102, "job": "api-tests", "status": "failed", "duration": 79},
      {"id": 103, "job": "lint", "status": "passed", "duration": 12}]}

A plain list is also accepted. Statuses passed/pass/success/succeeded and
failed/fail/failure/error/errored/timed_out are counted; skipped, cancelled
and queued records are ignored. The list is sorted by rate, then by failure
count, then by job name, and only jobs above --threshold (default 20 percent)
are printed.

Usage:
    python3 pipeline_flake.py runs.json
    python3 pipeline_flake.py runs.json --threshold 10
    export job records from your CI API, one record per job per run
    python3 pipeline_flake.py runs.json --help

Exit codes: 0 no job above the threshold, 1 at least one job above it,
2 usage or unreadable, missing or invalid input.

CI (a weekly flake gate):
    python3 pipeline_flake.py runs.json --threshold 20 || exit 1

Cron (Mondays at 07:10):
    10 7 * * 1 python3 /opt/s0sta/pipeline_flake.py /var/lib/ci/runs.json

The report is read-only. It counts what the history says, so a job that was
rerun after a failure looks worse here than in the UI; keep reruns in the
export or the rate is understated. A flaky job is a symptom: the rate says
which job to fix first, not why it fails.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys

PASS = {"passed", "pass", "success", "succeeded", "ok", "green"}
FAIL = {"failed", "fail", "failure", "error", "errored", "timed_out",
        "timedout", "red"}
IGNORE = {"skipped", "cancelled", "canceled", "queued", "neutral", "unknown"}


class FlakeError(Exception):
    """Anything that should end the run with exit code 2."""


def load_runs(path):
    """Return the run list from a path, or raise FlakeError."""
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except OSError as exc:
        raise FlakeError("cannot read %s: %s" % (path, exc))
    except ValueError as exc:
        raise FlakeError("%s is not valid JSON: %s" % (path, exc))
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict) and isinstance(doc.get("runs"), list):
        return doc["runs"]
    raise FlakeError("expected a runs list or an object with a runs list")


def count_runs(runs):
    """Return (counts by job, terminal records, ignored records)."""
    counts = {}
    terminal = 0
    ignored = 0
    for index, run in enumerate(runs, 1):
        if not isinstance(run, dict):
            raise FlakeError("run %d is not an object" % index)
        job = run.get("job")
        status = run.get("status")
        if not isinstance(job, str) or not job.strip():
            raise FlakeError("run %d has no job name" % index)
        if not isinstance(status, str):
            raise FlakeError("run %d (%s) has no status" % (index, job))
        state = status.strip().lower()
        if state in IGNORE:
            ignored += 1
            continue
        if state not in PASS and state not in FAIL:
            raise FlakeError("run %d (%s) has unknown status %r" % (index, job, status))
        terminal += 1
        counters = counts.setdefault(job, [0, 0])
        counters[0 if state in PASS else 1] += 1
    return counts, terminal, ignored


def flaky_jobs(counts):
    """Return (rate, failures, total, job) for jobs with both outcomes."""
    found = []
    for job, (passed, failed) in counts.items():
        if passed and failed:
            total = passed + failed
            found.append((failed / total, failed, total, job))
    found.sort(key=lambda item: (-item[0], -item[1], item[3]))
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rank CI jobs by flake rate and fail the run above a "
                    "threshold.",
        epilog="Exit codes: 0 clean, 1 flaky job above threshold, 2 usage or input error.")
    parser.add_argument("history", help="CI run history JSON")
    parser.add_argument("--threshold", type=float, default=20.0, metavar="PCT",
                        help="fail when a flake rate is above this percent (default 20)")
    args = parser.parse_args(argv)
    if not 0 <= args.threshold <= 100:
        parser.error("--threshold must be between 0 and 100")

    try:
        counts, terminal, ignored = count_runs(load_runs(args.history))
    except FlakeError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    found = flaky_jobs(counts)
    over = [item for item in found if item[0] > args.threshold / 100.0]
    if not over:
        print("OK no flaky job over %g%% in %d runs" % (args.threshold, terminal))
        return 0
    word = "job" if len(over) == 1 else "jobs"
    print("SCAN %d runs, %d %s over %g%%" % (terminal, len(over), word, args.threshold))
    for rate, _failed, _total, job in over:
        print("FLAKY %s %d%% failed" % (job, round(rate * 100)))
    if ignored:
        print("NOTE %d records ignored" % ignored)
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
