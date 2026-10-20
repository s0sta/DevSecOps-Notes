#!/usr/bin/env python3
"""dockerfile_lint.py - six line-based checks on a Dockerfile.

Checks:
    DF001  FROM without a tag or digest
    DF002  no USER instruction, or USER is root
    DF003  ADD where COPY would do
    DF004  no HEALTHCHECK, or HEALTHCHECK NONE
    DF005  apt-get install without --no-install-recommends
    DF006  a secret-looking ENV or ARG that carries a value

Usage:
    python3 dockerfile_lint.py Dockerfile
    python3 dockerfile_lint.py deploy/Dockerfile api/Dockerfile
    python3 dockerfile_lint.py --quiet Dockerfile
    python3 dockerfile_lint.py --list-rules

CI (before the build):
    python3 dockerfile_lint.py Dockerfile || exit 1
    docker build -t api:1.0 .

Cron (weekly review of every Dockerfile in a tree):
    0 6 * * 1 find /srv/app -name Dockerfile -print0 | xargs -0 python3 /opt/scripts/dockerfile_lint.py -q

Exit codes: 0 clean, 1 findings, 2 usage or input error.
Read-only: every file is opened for reading and nothing is written.
Line-based: continuation lines are joined, and comments are skipped.

By s0sta.com
"""
import argparse
import re
import sys

RULES = (
    ("DF001", "FROM without a tag or digest"),
    ("DF002", "no USER instruction, or USER is root"),
    ("DF003", "ADD where COPY would do"),
    ("DF004", "no HEALTHCHECK, or HEALTHCHECK NONE"),
    ("DF005", "apt-get install without --no-install-recommends"),
    ("DF006", "a secret-looking ENV or ARG that carries a value"),
)

SECRET = re.compile(
    r"SECRET|TOKEN|PASSWORD|PASSWD|(?:^|_)PASS(?:$|_)|API_?KEY|ACCESS_KEY"
    r"|PRIVATE_KEY|CREDENTIAL", re.I)
APT = re.compile(r"\bapt(?:-get)?\b.*\binstall\b", re.I)
INSTRUCTION = re.compile(r"(\S+)\s*(.*)")


def logical_lines(path):
    """Yield (first line number, instruction) with continuations joined."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        buffer, start = "", None
        for number, raw in enumerate(handle, 1):
            stripped = raw.rstrip("\r\n").strip()
            if start is None:
                if not stripped or stripped.startswith("#"):
                    continue
                start = number
                buffer = stripped
            else:
                if not stripped or stripped.startswith("#"):
                    continue
                buffer = buffer + " " + stripped
            if buffer.endswith("\\"):
                buffer = buffer[:-1].rstrip()
                continue
            yield start, buffer
            buffer, start = "", None
        if start is not None:
            yield start, buffer


def parse(instruction):
    """Return (KEYWORD, rest) for one instruction."""
    match = INSTRUCTION.match(instruction.strip())
    if not match:
        return "", ""
    return match.group(1).upper(), match.group(2).strip()


def image_and_stage(rest):
    """Return (image, stage) from a FROM line, ignoring --platform flags."""
    parts = rest.split()
    image = ""
    for part in parts:
        if not part.startswith("-"):
            image = part
            break
    stage = ""
    for index, part in enumerate(parts):
        if part.upper() == "AS" and index + 1 < len(parts):
            stage = parts[index + 1]
    return image, stage


def is_pinned(image, stages):
    """True when image is a digest, a local stage name, or scratch."""
    if not image:
        return True
    if image.lower() == "scratch" or image in stages:
        return True
    if "@" in image:
        return True
    return ":" in image.rsplit("/", 1)[-1]


def assignments(rest):
    """Yield (name, value) from the arguments of ENV or ARG."""
    tokens = rest.split()
    if not tokens:
        return
    if "=" not in tokens[0]:
        yield tokens[0], " ".join(tokens[1:])
        return
    for token in tokens:
        if "=" not in token:
            continue
        name, _, value = token.partition("=")
        yield name, value


def add_is_copy(rest):
    """True when ADD only moves local files, so COPY would do."""
    parts = [part for part in rest.split() if not part.startswith("--")]
    if len(parts) < 2:
        return False
    for source in parts[:-1]:
        low = source.lower()
        if low.startswith(("http://", "https://")):
            return False
        if low.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".zip")):
            return False
    return True


def secret_finding(number, rest, keyword):
    """Return one DF006 finding, or None."""
    for name, value in assignments(rest):
        if not value.strip().strip("'\""):
            continue
        if SECRET.search(name):
            return (number, "DF006",
                    "%s %s carries a value; use a BuildKit secret" % (keyword, name))
    return None


def check_file(path):
    """Return a list of (line or None, code, message) for one Dockerfile."""
    findings = []
    stages = set()
    user, user_line = None, None
    health = None

    for number, instruction in logical_lines(path):
        keyword, rest = parse(instruction)
        flat = " ".join(rest.split())

        if keyword == "FROM":
            image, stage = image_and_stage(rest)
            if not is_pinned(image, stages):
                findings.append((number, "DF001",
                                 "FROM without a tag or digest: %s" % image))
            if stage:
                stages.add(stage)
        elif keyword == "USER":
            user, user_line = flat, number
        elif keyword == "HEALTHCHECK":
            health = (number, flat.upper() == "NONE")
        elif keyword == "ADD" and add_is_copy(rest):
            findings.append((number, "DF003",
                             "ADD where COPY would do: %s" % flat[:40]))
        elif keyword in ("ENV", "ARG"):
            hit = secret_finding(number, rest, keyword)
            if hit:
                findings.append(hit)
        elif APT.search(flat) and "--no-install-recommends" not in flat:
            findings.append((number, "DF005",
                             "apt-get install without --no-install-recommends"))

    if health is None:
        findings.append((None, "DF004", "no HEALTHCHECK instruction"))
    elif health[1]:
        findings.append((health[0], "DF004", "HEALTHCHECK NONE disables the check"))

    if user is None:
        findings.append((None, "DF002",
                         "no USER instruction; the container runs as root"))
    elif user.split(":")[0].strip().lower() in ("root", "0"):
        findings.append((user_line, "DF002", "USER is root: %s" % user))

    findings.sort(key=lambda item: (item[0] is None, item[0] or 0, item[1]))
    return findings


def show(path, findings, quiet):
    """Print findings and the per-file summary."""
    if not quiet:
        for line, code, message in findings:
            where = "%s:%d" % (path, line) if line else path
            print("%s: %s %s" % (where, code, message))
    if findings:
        print("%d finding%s in %s"
              % (len(findings), "" if len(findings) == 1 else "s", path))
    else:
        print("%s: OK" % path)


def main():
    parser = argparse.ArgumentParser(
        prog="dockerfile_lint.py",
        description="Six line-based checks on a Dockerfile.",
        epilog="Read-only. Exit 0 clean, 1 findings, 2 usage or input error.",
    )
    parser.add_argument("files", nargs="*", metavar="DOCKERFILE",
                        help="Dockerfile to check")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    parser.add_argument("--list-rules", action="store_true",
                        help="print the rule table and exit")
    args = parser.parse_args()

    if args.list_rules:
        for code, title in RULES:
            print("%s  %s" % (code, title))
        return 0
    if not args.files:
        parser.error("give at least one Dockerfile, or --list-rules")

    total, broken = 0, False
    for path in args.files:
        try:
            findings = check_file(path)
        except OSError as exc:
            print("error: %s: %s" % (path, exc.strerror or exc), file=sys.stderr)
            broken = True
            continue
        show(path, findings, args.quiet)
        total += len(findings)

    if broken:
        return 2
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
