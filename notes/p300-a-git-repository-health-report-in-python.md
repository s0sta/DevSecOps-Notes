---
id: p300
title: "A git repository health report in Python"
slug: a-git-repository-health-report-in-python
sections: [devsecops]
topic: "Python scripts"
tags: [Git, Python, DevOps, SRE, Engineering]
source: "LinkedIn post P300 · Visual series"
linkedin_date: 2028-08-27
design: code
script: git_health.py
---

# A git repository health report in Python

One person knows where the deploy scripts live, and they are on holiday. A repository's health is measurable: who commits, how often, and how long since anyone did.

## Quick reference

The full script is at the end of this note: **git_health.py** (standard library only, no `pip install`).

**Run it**

```bash
python3 git_health.py
```

**Example output**

```text
bus factor 1 of 3 authors
FAIL: bus factor is 1
```

## Explained

### What it reports

The script runs git log with `--pretty=format:'%an|%ad' --date=short`, or reads the same text from a file. The full script is attached: standard library only, read-only. It prints commits per month for the last six months, the top three authors with their share, the bus factor, and the age of the last commit.

### Bus factor

The bus factor is the smallest number of authors whose commits together exceed half the total. One name above fifty percent means a bus factor of one, and that is where a hiring plan should start.

### Exit codes

Exit 0 when the bus factor is at least two and the last commit is inside ninety days, exit 1 when either fails, exit 2 when git cannot read the repository. Exit 2 is not a finding: it means the tool could not answer, and a pipeline should treat it as broken. Run it monthly from cron, or in CI on the default branch. The age limit is yours to set with `--stale-days`.

> **The honest caveat:** commit counts measure activity, not knowledge. The person who reviews every change may never appear in git log, and merge commits inflate whoever pressed the button.

> **The lesson:** a repository with one author is a single point of failure that no dashboard shows.

## In one line

> **One author is a single point.** A repository is a team asset, not a personal one.

**Run it monthly**

```bash
0 9 1 * * python3 git_health.py /srv/repo
```

## Script: git_health.py

Download: [scripts/git_health.py](../scripts/git_health.py)

```python
#!/usr/bin/env python3
"""git_health.py - a one-page health report for a Git repository.

Runs `git log --pretty=format:'%an|%ad' --date=short` (or reads the same
text from a saved file) and reports:

    - commits per month for the last N months
    - the top authors and their share of commits
    - the bus factor: the smallest number of authors whose commits
      together exceed half of the total
    - the age of the last commit

Exit codes: 0 healthy, 1 bus factor is 1 or the repository is stale,
2 usage or input error (including a repository with no commits).
Read-only: it runs git log and reads one file; nothing is written.

Usage:
    python3 git_health.py
    python3 git_health.py /srv/app
    python3 git_health.py /srv/app --months 12 --stale-days 120
    python3 git_health.py --log saved.log --top 5
    python3 git_health.py /srv/app --quiet

Save the log once and report on it later:
    git log --pretty=format:'%an|%ad' --date=short > /tmp/git.log
    python3 git_health.py --log /tmp/git.log

CI (fail a job on a lone maintainer or a stale default branch):
    python3 git_health.py . || exit 1

Cron (first of the month, 09:00):
    0 9 1 * * python3 /opt/scripts/git_health.py /srv/app >> /var/log/git_health.log 2>&1

By s0sta.com
"""
import argparse
import os
import subprocess
import sys
from collections import Counter
from datetime import date

LOG_FORMAT = "%an|%ad"


class InputError(Exception):
    """Anything that should end the run with exit code 2."""


def read_git_log(repo):
    """Return the raw git log text for repo, or raise InputError."""
    command = ["git", "-C", repo, "log",
               "--pretty=format:" + LOG_FORMAT, "--date=short"]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        raise InputError("git is not installed or not on PATH")
    except OSError as exc:
        raise InputError("could not run git: %s" % exc)
    except subprocess.TimeoutExpired:
        raise InputError("git log timed out after 120 seconds")
    if proc.returncode != 0:
        message = (proc.stderr or "").strip().splitlines()
        raise InputError(message[-1] if message else "git log failed")
    return proc.stdout


def parse_log(text):
    """Return [(author, ISO date)] from author|date lines, or raise InputError."""
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if "|" not in line:
            raise InputError("line %d is not author|date: %s" % (number, line[:60]))
        author, _, when = line.rpartition("|")
        author, when = author.strip(), when.strip()[:10]
        if not author:
            raise InputError("line %d has no author" % number)
        try:
            date.fromisoformat(when)
        except ValueError:
            raise InputError("line %d has no ISO date: %s" % (number, when))
        rows.append((author, when))
    if not rows:
        raise InputError("no commits found")
    return rows


def months_back(today, count):
    """Return the last count months as YYYY-MM strings, oldest first."""
    year, month = today.year, today.month
    out = []
    for _ in range(count):
        out.append("%04d-%02d" % (year, month))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(out))


def bus_factor(counts, total):
    """Smallest number of top authors whose commits exceed half of total."""
    running = 0
    for index, (_, count) in enumerate(counts, 1):
        running += count
        if running * 2 > total:
            return index
    return 0


def age_text(days):
    """Return a short English age for the last commit."""
    if days <= 0:
        return "today"
    if days == 1:
        return "1 day ago"
    return "%d days ago" % days


def report(args, rows):
    """Print the report and return the exit code."""
    total = len(rows)
    counts = Counter(author for author, _ in rows).most_common()
    last = max(when for _, when in rows)
    age = (date.today() - date.fromisoformat(last)).days
    if age < 0:
        age = 0
    bus = bus_factor(counts, total)

    bus_line = "%d of %d author%s" % (bus, len(counts),
                                      "" if len(counts) == 1 else "s")
    source = args.log if args.log else os.path.abspath(args.repo)
    print("git_health: %s" % source)
    for label, value in (("commits", total),
                         ("authors", len(counts)),
                         ("last commit", "%s (%s)" % (last, age_text(age))),
                         ("bus factor", bus_line)):
        print("%-11s %s" % (label, value))

    if not args.quiet:
        per_month = Counter(when[:7] for _, when in rows)
        window = months_back(date.today(), args.months)
        peak = max([per_month.get(month, 0) for month in window] or [1]) or 1
        print("\nCommits per month (last %d)" % args.months)
        for month in window:
            count = per_month.get(month, 0)
            bar = "#" * max(1, round(20 * count / peak)) if count else ""
            print("%s  %-20s %d" % (month, bar, count))

        print("\nTop authors")
        for index, (author, count) in enumerate(counts[:args.top], 1):
            share = round(100 * count / total)
            print("%d. %-22s %4d  %3d%%" % (index, author[:22], count, share))

    failures = []
    if bus < 2:
        failures.append("bus factor is %d" % bus)
    if age > args.stale_days:
        failures.append("last commit is %d days old (limit %d)"
                        % (age, args.stale_days))
    if failures:
        for failure in failures:
            print("FAIL: %s" % failure)
        return 1
    print("OK: bus factor %d, last commit %s" % (bus, age_text(age)))
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="git_health.py",
        description="Report commits per month, top authors, bus factor and last commit age.",
        epilog="Read-only. Exit 0 healthy, 1 bus factor 1 or stale, 2 input error.",
    )
    parser.add_argument("repo", nargs="?", default=".",
                        help="repository path (default: current directory)")
    parser.add_argument("-l", "--log", metavar="FILE",
                        help="read a saved git log (author|date lines) instead of running git")
    parser.add_argument("-m", "--months", type=int, default=6,
                        help="months to show (default 6)")
    parser.add_argument("-t", "--top", type=int, default=3,
                        help="authors to list (default 3)")
    parser.add_argument("-s", "--stale-days", type=int, default=90,
                        help="fail when the last commit is older than this (default 90)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args()

    if args.months < 1:
        parser.error("--months must be at least 1")
    if args.top < 1:
        parser.error("--top must be at least 1")
    if args.stale_days < 0:
        parser.error("--stale-days cannot be negative")
    if not args.log and not os.path.isdir(args.repo):
        print("error: not a directory: %s" % args.repo, file=sys.stderr)
        return 2

    try:
        if args.log:
            try:
                with open(args.log, encoding="utf-8", errors="replace") as handle:
                    raw = handle.read()
            except OSError as exc:
                raise InputError("cannot read %s: %s" % (args.log, exc.strerror or exc))
        else:
            raw = read_git_log(args.repo)
        rows = parse_log(raw)
    except InputError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return report(args, rows)


if __name__ == "__main__":
    sys.exit(main())
```
