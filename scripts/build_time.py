#!/usr/bin/env python3
"""build_time.py - rank CI jobs and fail on a slow build or a regression.

Reads a JSON export of CI jobs. The export is either a list of jobs or an
object with a "jobs" list. Each job needs:
    name      the job name
    duration  wall-clock seconds, as a number
    status    the CI status, for example success, failed or cancelled

Durations are compared per job name. When a name appears more than once, the
baseline keeps its slowest run, so a matrix leg is compared against a real run
rather than an average.

Usage:
    python3 build_time.py jobs.json
    python3 build_time.py jobs.json --threshold 600
    python3 build_time.py jobs.json --baseline yesterday.json
    python3 build_time.py jobs.json --baseline yesterday.json --regression 15
    python3 build_time.py jobs.json --top 5 --quiet

CI (after the build, keeping the export for the next run):
    python3 build_time.py jobs.json --threshold 600 || exit 1

Cron (a weekly look at the slowest jobs):
    0 7 * * 1 python3 /opt/scripts/build_time.py /var/lib/ci/jobs.json --top 10

Exit codes: 0 within budget, 1 over the threshold or a regression,
2 usage or input error.
Read-only: every file is opened for reading and nothing is written.

By s0sta.com
"""
import argparse
import json
import sys


def load_jobs(path):
    """Return a list of jobs from one export, or raise ValueError."""
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc.strerror or exc))
    except UnicodeDecodeError as exc:
        raise ValueError("%s is not UTF-8 text: %s" % (path, exc.reason))
    except json.JSONDecodeError as exc:
        raise ValueError("%s is not valid JSON: line %d column %d"
                         % (path, exc.lineno, exc.colno))
    if isinstance(data, dict):
        data = data.get("jobs")
    if not isinstance(data, list):
        raise ValueError("%s: expected a list of jobs or an object with a "
                         "jobs list" % path)
    jobs = []
    for index, item in enumerate(data, 1):
        if not isinstance(item, dict):
            raise ValueError("%s: job %d is not an object" % (path, index))
        name = item.get("name")
        duration = item.get("duration")
        status = item.get("status", "unknown")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("%s: job %d has no name" % (path, index))
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise ValueError("%s: job %s has no numeric duration"
                             % (path, name))
        if duration < 0:
            raise ValueError("%s: job %s has a negative duration"
                             % (path, name))
        jobs.append({"name": name.strip(), "duration": float(duration),
                     "status": str(status)})
    if not jobs:
        raise ValueError("%s: the export contains no jobs" % path)
    return jobs


def baseline_map(jobs):
    """Return {job name: slowest duration} for one export."""
    slowest = {}
    for job in jobs:
        name = job["name"]
        slowest[name] = max(slowest.get(name, 0.0), job["duration"])
    return slowest


def delta_text(duration, was):
    """Return a readable change against the baseline."""
    if not was:
        return "new"
    change = duration - was
    return "%+.0fs (%+.0f%%)" % (change, change / was * 100.0)


def report(jobs, base, threshold, regression, top, quiet):
    """Print the ranking and the summary, and return the exit code."""
    rows = sorted(jobs, key=lambda job: -job["duration"])
    over, slower = set(), set()
    for index, job in enumerate(rows):
        was = base.get(job["name"], 0.0)
        if threshold is not None and job["duration"] > threshold:
            over.add(index)
        if was and job["duration"] > was * (1.0 + regression / 100.0):
            slower.add(index)

    if not quiet:
        print("%-26s %7s  %-9s %9s  %-14s %s"
              % ("JOB", "SECONDS", "STATUS", "BASELINE", "DELTA", "FLAG"))
        for index, job in enumerate(rows[:top]):
            was = base.get(job["name"], 0.0)
            flags = []
            if index in slower:
                flags.extend(["!", "REGRESSION"])
            if index in over:
                flags.append("OVER")
            line = ("%-26s %7.0f  %-9s %9s  %-14s %s"
                    % (job["name"][:26], job["duration"],
                       job["status"][:9], ("%.0fs" % was) if was else "-",
                       delta_text(job["duration"], was) if base else "-",
                       " ".join(flags)))
            print(line.rstrip())

    parts = ["checked %d job%s" % (len(rows), "" if len(rows) == 1 else "s")]
    if threshold is not None:
        parts.append("%d over %gs" % (len(over), threshold))
    if base:
        parts.append("%d regression%s"
                     % (len(slower), "" if len(slower) == 1 else "s"))
    print(", ".join(parts))
    return 1 if over or slower else 0


def main():
    parser = argparse.ArgumentParser(
        prog="build_time.py",
        description="Rank CI jobs by duration and fail on a threshold or a "
                    "regression.",
        epilog="Read-only. Exit 0 clean, 1 over threshold or regression, "
               "2 usage or input error.",
    )
    parser.add_argument("export", metavar="JOBS.json",
                        help="CI jobs JSON export")
    parser.add_argument("--baseline", metavar="PREV.json",
                        help="earlier export to compare against")
    parser.add_argument("--threshold", type=float, metavar="SECONDS",
                        help="fail when any job is slower than this")
    parser.add_argument("--regression", type=float, default=20.0,
                        metavar="PERCENT",
                        help="fail when a job is this much slower than the "
                             "baseline (default 20)")
    parser.add_argument("--top", type=int, default=10, metavar="N",
                        help="print only the N slowest jobs (default 10)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args()

    if args.threshold is not None and args.threshold < 0:
        parser.error("--threshold cannot be negative")
    if args.regression < 0:
        parser.error("--regression cannot be negative")
    if args.top < 1:
        parser.error("--top must be at least 1")

    try:
        jobs = load_jobs(args.export)
        base = baseline_map(load_jobs(args.baseline)) if args.baseline else {}
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return report(jobs, base, args.threshold, args.regression, args.top,
                  args.quiet)


if __name__ == "__main__":
    sys.exit(main())
