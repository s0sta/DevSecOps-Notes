#!/usr/bin/env python3
"""repo_standards.py - score a repository against seven baseline standards.

Checks that a repository root has the files a service needs before its first
deploy: a README, a licence, a security policy, CI, CODEOWNERS, tests and a
lockfile. Prints a score out of 100 and exits 1 when the score is below the
threshold, so a new service cannot start life without the basics.

Usage:
    python3 repo_standards.py                  # checks the current directory
    python3 repo_standards.py path/to/repo     # checks another repository
    python3 repo_standards.py . --json         # machine-readable result
    python3 repo_standards.py . --min-score 80 # ratchet, do not block yet

CI (GitHub Actions step):
    - run: python3 repo_standards.py . --min-score 100

Cron (weekly, Monday 07:00):
    0 7 * * 1 cd /srv/repos && python3 repo_standards.py . >> /var/log/repo.log 2>&1

Read-only: it only looks for files and never writes to the repository.
By s0sta.com
"""
import argparse
import json
import sys
from pathlib import Path

README = ("README.md", "README.rst", "README.txt", "README", "readme.md")
LICENCE = ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md",
           "COPYING", "COPYING.md")
SECURITY = ("SECURITY.md", ".github/SECURITY.md", "SECURITY.rst",
            "docs/SECURITY.md")
OWNERS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")
LOCKFILES = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
             "poetry.lock", "Pipfile.lock", "uv.lock", "go.sum", "Cargo.lock",
             "composer.lock", "Gemfile.lock", "mix.lock", "pubspec.lock",
             "packages.lock.json", "flake.lock")
TEST_DIRS = ("tests", "test", "spec", "__tests__")
TEST_FILES = ("test_*.py", "*_test.go", "*.test.js", "*.test.ts", "*.spec.ts",
              "*_test.rs")
CI_FILES = (".gitlab-ci.yml", "Jenkinsfile", ".circleci/config.yml",
            "azure-pipelines.yml", "bitbucket-pipelines.yml", ".drone.yml",
            ".buildkite/pipeline.yml")


def first_file(root, names):
    """Return the first existing relative path, or None."""
    for name in names:
        if (root / name).is_file():
            return name
    return None


def find_ci(root):
    workflows = root / ".github" / "workflows"
    try:
        if workflows.is_dir():
            for p in sorted(workflows.iterdir()):
                if p.is_file() and p.suffix in (".yml", ".yaml"):
                    return p.relative_to(root).as_posix()
    except OSError:
        pass
    return first_file(root, CI_FILES)


def find_tests(root):
    for name in TEST_DIRS:
        if (root / name).is_dir():
            return name + "/"
    for pattern in TEST_FILES:
        for p in sorted(root.glob(pattern)):
            if p.is_file():
                return p.name
    return None


def find_lockfile(root):
    return first_file(root, LOCKFILES)


def collect(root):
    checks = [
        ("README", first_file(root, README)),
        ("LICENCE", first_file(root, LICENCE)),
        ("SECURITY", first_file(root, SECURITY)),
        ("CI", find_ci(root)),
        ("CODEOWNERS", first_file(root, OWNERS)),
        ("TESTS", find_tests(root)),
        ("LOCKFILE", find_lockfile(root)),
    ]
    rows = []
    for name, found in checks:
        rows.append({"name": name, "ok": found is not None,
                     "detail": found or "not found"})
    passed = sum(1 for r in rows if r["ok"])
    score = int(round(100.0 * passed / len(rows)))
    return rows, score


def main():
    ap = argparse.ArgumentParser(
        prog="repo_standards.py",
        description="Score a repository against seven baseline standards.")
    ap.add_argument("root", nargs="?", default=".",
                    help="repository root to check (default: current directory)")
    ap.add_argument("--json", action="store_true",
                    help="print the result as JSON")
    ap.add_argument("--min-score", type=int, default=100, metavar="N",
                    help="minimum passing score, 0-100 (default: 100)")
    args = ap.parse_args()

    if not 0 <= args.min_score <= 100:
        ap.error("--min-score must be between 0 and 100")

    root = Path(args.root).expanduser()
    if not root.exists():
        ap.error("not found: %s" % root)
    if not root.is_dir():
        ap.error("not a directory: %s" % root)

    rows, score = collect(root)
    missing = [r["name"] for r in rows if not r["ok"]]
    ok = score >= args.min_score

    if args.json:
        print(json.dumps({
            "root": str(root.resolve()),
            "score": score,
            "passed": len(rows) - len(missing),
            "total": len(rows),
            "checks": rows,
            "missing": missing,
            "ok": ok,
        }, indent=2))
    else:
        print("repo standards  %s" % root.resolve())
        print()
        for r in rows:
            mark = "ok  " if r["ok"] else "MISS"
            print("[%s] %-11s %s" % (mark, r["name"], r["detail"]))
        print()
        print("score %d/100 (%d/%d)" % (score, len(rows) - len(missing), len(rows)))
        if missing and ok:
            print("PASS at min-score %d, still missing: %s"
                  % (args.min_score, ", ".join(missing)))
        elif missing:
            print("FAIL missing: " + ", ".join(missing))
        else:
            print("OK all standards present")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
