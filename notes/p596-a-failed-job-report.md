---
id: p596
title: "A failed job report"
slug: a-failed-job-report
sections: [devsecops]
topic: "Python scripts"
tags: [Kubernetes, Python, CICD, SRE, DevOps]
source: "LinkedIn post P596 · PythonFixes series"
linkedin_date: 2030-07-18
design: code
script: job_failures.py
---

# A failed job report

On Monday the nightly ETL is missing. The CronJob still schedules, so every dashboard is green. It failed on Friday and nothing paged.

## Quick reference

The full script is at the end of this note: `job_failures.py` (standard library only, no `pip install`).

**Run it**

```bash
python3 job_failures.py /tmp/jobs.json
```

**Example output**

```text
JOB nightly-etl failed 6
ALERT 2 failed, 1 suspended
```

## Explained

### What it does

The script reads the output of kubectl get jobs,cronjobs -A -o json. It prints each failed Job with its count and terminal reason, sorts by failure count, lists suspended CronJobs and exits 1.

### What the screen shows

The 14 visible lines split Jobs from CronJobs, read status.failed and spec.suspend, then print the worst Job and the summary. On the fixture they print JOB nightly-etl failed 6, then ALERT 2 failed, 1 suspended.

### How to run it

`python3 job_failures.py /tmp/jobs.json`. Exit 0 is clean, 1 is a failed Job or suspended CronJob, 2 is bad input.

### The fix

Read the failed pod's log with kubectl logs job/nightly-etl -n batch, fix the cause, then delete the Job so the next run starts clean. Deleting a Job also deletes its pods and their logs, so read them first. Confirm a suspended CronJob with its owner before resuming it.

### Prevention

Alert on a Job condition Failed and on spec.suspend, and check status.lastSuccessfulTime every morning. A schedule that runs is not a job that succeeds.

> **The honest caveat:** a recreated Job loses its history, and an old failed Job may already be fixed. Suspended can be deliberate; confirm before resuming.

> **The lesson:** a failed job is a silent outage.

## In one line

> **A failed job is a silent outage.** The schedule keeps running; the work does not.

**Rank the jobs**

```bash
python3 job_failures.py /tmp/jobs.json
```

## Script: job_failures.py

Download: [scripts/job_failures.py](../scripts/job_failures.py)

```python
#!/usr/bin/env python3
"""Rank failed Jobs and list suspended CronJobs from a kubectl JSON dump.

Reads one read-only export of both kinds:

    kubectl get jobs,cronjobs -A -o json > /tmp/jobs.json
    python3 job_failures.py /tmp/jobs.json

For every Job it reports status.failed and the terminal condition:

    BackoffLimitExceeded   the Job retried spec.backoffLimit times and gave up
    DeadlineExceeded       activeDeadlineSeconds ran out
    Error                  another Failed condition, or failures with no reason

Jobs are ranked by failure count. A Job whose failed count reached its
backoffLimit is marked even when the condition is missing. Suspended
CronJobs are listed separately: a suspended schedule is a silent outage,
not a clean one.

Usage:
    python3 job_failures.py
    python3 job_failures.py /tmp/jobs.json
    kubectl get jobs,cronjobs -A -o json | python3 job_failures.py -
    python3 job_failures.py /tmp/jobs.json --verbose

Exit codes: 0 no failed Job and no suspended CronJob, 1 at least one
finding, 2 usage, unreadable or invalid input.

CI (fail the nightly check when a batch Job has failed):
    kubectl get jobs,cronjobs -A -o json > /tmp/jobs.json
    python3 job_failures.py /tmp/jobs.json || exit 1

Cron (daily at 07:30, before the morning review):
    30 7 * * * kubectl get jobs,cronjobs -A -o json | python3 /opt/s0sta/job_failures.py -

Read-only: it reads one local file or stdin and never calls the API
server. A failed Job is a fact, not a cause: the pod logs and the
container exit code are still the evidence. A suspended CronJob may be
deliberate, so confirm with the owner before resuming it.

Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys


class JobError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source):
    try:
        if source == "-":
            return json.load(sys.stdin)
        with open(source, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise JobError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise JobError("%s is not JSON: %s" % (source, exc))


def as_dict(value, label):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise JobError("%s must be an object" % label)
    return value


def as_list(value, label):
    if value is None:
        return []
    if not isinstance(value, list):
        raise JobError("%s must be a list" % label)
    return value


def items_of(doc, label):
    if not isinstance(doc, dict):
        raise JobError("%s must be a JSON object" % label)
    items = doc.get("items")
    if items is not None:
        return as_list(items, "%s items" % label)
    if "metadata" in doc or "kind" in doc:
        return [doc]
    raise JobError("%s has no items list and no metadata" % label)


def identity(obj, number):
    if not isinstance(obj, dict):
        raise JobError("object %d is not an object" % number)
    metadata = as_dict(obj.get("metadata"), "object %d metadata" % number)
    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        raise JobError("object %d has no metadata.name" % number)
    namespace = metadata.get("namespace") or "default"
    return str(namespace), name


def integer(value, label, default=0):
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        raise JobError("%s must be an integer" % label)
    return value


def condition_of(status, wanted):
    conditions = as_list(status.get("conditions"), "status.conditions")
    for index, cond in enumerate(conditions, 1):
        if not isinstance(cond, dict):
            raise JobError("condition %d is not an object" % index)
        if cond.get("type") == wanted:
            return str(cond.get("status") or ""), str(cond.get("reason") or ""), \
                str(cond.get("message") or "")
    return "", "", ""


def job_record(obj, number):
    namespace, name = identity(obj, number)
    spec = as_dict(obj.get("spec"), "Job %s spec" % name)
    status = as_dict(obj.get("status"), "Job %s status" % name)
    failed = integer(status.get("failed"), "Job %s status.failed" % name)
    backoff = integer(spec.get("backoffLimit"), "Job %s spec.backoffLimit" % name,
                      6)
    failed_status, reason, message = condition_of(status, "Failed")
    exhausted = failed > 0 and failed >= backoff
    if failed_status != "True" and not exhausted:
        return None
    if not reason and exhausted:
        reason = "BackoffLimitExceeded"
    return {
        "namespace": namespace,
        "name": name,
        "failed": failed,
        "backoff": backoff,
        "reason": reason,
        "message": message,
    }


def cron_record(obj, number):
    namespace, name = identity(obj, number)
    spec = as_dict(obj.get("spec"), "CronJob %s spec" % name)
    if spec.get("suspend") is not True:
        return None
    return {"namespace": namespace, "name": name}


def plural(count, one, many):
    return one if count == 1 else many


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rank failed Jobs and list suspended CronJobs.",
        epilog="Exit codes: 0 clean, 1 findings, 2 usage or input error.")
    parser.add_argument("objects", nargs="?", default="-",
                        help="kubectl get jobs,cronjobs -A -o json output, or -")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the terminal condition message")
    args = parser.parse_args(argv)

    try:
        items = items_of(read_json(args.objects), "job dump")
        jobs = []
        crons = []
        for number, obj in enumerate(items, 1):
            if not isinstance(obj, dict):
                raise JobError("object %d is not an object" % number)
            kind = str(obj.get("kind") or "")
            if kind == "Job":
                record = job_record(obj, number)
                if record is not None:
                    jobs.append(record)
            elif kind == "CronJob":
                record = cron_record(obj, number)
                if record is not None:
                    crons.append(record)
    except JobError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if not jobs and not crons:
        print("OK no failed jobs or suspended cronjobs in %d objects"
              % len(items))
        return 0

    jobs.sort(key=lambda job: (-job["failed"], job["namespace"], job["name"]))
    for job in jobs:
        limit = "/%d" % job["backoff"] if job["backoff"] else ""
        suffix = " %s" % job["reason"] if job["reason"] else ""
        print("JOB %s/%s failed=%d%s%s" % (
            job["namespace"], job["name"], job["failed"], limit, suffix))
        if args.verbose and job["message"]:
            print("  %s" % job["message"])
    for cron in sorted(crons, key=lambda c: (c["namespace"], c["name"])):
        print("CRONJOB %s/%s suspended" % (cron["namespace"], cron["name"]))

    parts = []
    if jobs:
        parts.append("%d failed %s" % (
            len(jobs), plural(len(jobs), "job", "jobs")))
    if crons:
        parts.append("%d suspended %s" % (
            len(crons), plural(len(crons), "cronjob", "cronjobs")))
    print("ALERT " + ", ".join(parts))
    return 1


if __name__ == "__main__":
    sys.exit(main())
```
