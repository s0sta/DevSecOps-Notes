#!/usr/bin/env python3
"""s3_public_check.py - flag public S3 bucket policies and ACL grants.

Reads two JSON documents and never calls AWS:

    the bucket policy   aws s3api get-bucket-policy --bucket b --query Policy \
                            --output text
    the bucket ACL      aws s3api get-bucket-acl --bucket b

A policy statement is public when Effect is Allow, Principal is "*" (also
{"AWS": "*"} or a list containing "*") and the statement has no Condition.
An ACL grant is public when its Grantee URI is the AllUsers or
AuthenticatedUsers group.

Usage:
    aws s3api get-bucket-policy --bucket demo --query Policy \
        --output text > /tmp/policy.json
    aws s3api get-bucket-acl --bucket demo > /tmp/acl.json
    python3 s3_public_check.py /tmp/policy.json --acl /tmp/acl.json
    python3 s3_public_check.py /tmp/policy.json
    python3 s3_public_check.py --acl /tmp/acl.json -q
    cat /tmp/policy.json | python3 s3_public_check.py -

Exit codes: 0 clean, 1 public access found, 2 usage or input error.

CI / cron (a non-zero exit fails the job):
    aws s3api get-bucket-policy --bucket demo --query Policy \
        --output text > /tmp/policy.json && \
    aws s3api get-bucket-acl --bucket demo > /tmp/acl.json && \
    python3 s3_public_check.py /tmp/policy.json --acl /tmp/acl.json

Read-only: the script opens local files (or stdin) and writes nothing.
Standard library only, Python 3.8+.

By s0sta.com
"""
import argparse
import json
import sys


class CheckError(Exception):
    """Anything that should end the run with exit code 2."""


def read_json(source, label):
    """Read one JSON document from a file or '-' for stdin."""
    if source == "-":
        try:
            return json.load(sys.stdin)
        except ValueError as exc:
            raise CheckError("%s from stdin is not JSON: %s" % (label, exc))
    try:
        with open(source) as handle:
            return json.load(handle)
    except OSError as exc:
        raise CheckError("cannot read %s: %s" % (source, exc))
    except ValueError as exc:
        raise CheckError("%s is not JSON: %s" % (source, exc))


def unwrap_policy(doc):
    """Accept a raw policy document or the get-bucket-policy response."""
    if not isinstance(doc, dict):
        raise CheckError("policy must be a JSON object")
    inner = doc.get("Policy")
    if isinstance(inner, str):
        try:
            doc = json.loads(inner)
        except ValueError as exc:
            raise CheckError("the Policy field is not JSON: %s" % exc)
    elif isinstance(inner, dict):
        doc = inner
    if not isinstance(doc, dict):
        raise CheckError("policy must be a JSON object")
    return doc


def statements_of(doc):
    """Return the policy statements as a list of objects."""
    statements = unwrap_policy(doc).get("Statement")
    if statements is None:
        return []
    if isinstance(statements, dict):
        return [statements]
    if not isinstance(statements, list):
        raise CheckError("Statement must be an object or a list")
    for statement in statements:
        if not isinstance(statement, dict):
            raise CheckError("every Statement must be an object")
    return statements


def principal_is_public(principal):
    """True for "*", {"AWS": "*"}, ["*"] and similar shapes."""
    if principal == "*":
        return True
    if isinstance(principal, list):
        return any(principal_is_public(item) for item in principal)
    if isinstance(principal, dict):
        return any(principal_is_public(value) for value in principal.values())
    return False


def has_condition(statement):
    """True when the statement carries a non-empty Condition block."""
    condition = statement.get("Condition")
    return isinstance(condition, dict) and bool(condition)


def check_policy(doc):
    """Return one finding per public Allow statement without a Condition."""
    findings = []
    for statement in statements_of(doc):
        if statement.get("Effect") != "Allow":
            continue
        if not principal_is_public(statement.get("Principal")):
            continue
        if has_condition(statement):
            continue
        sid = statement.get("Sid") or "(no sid)"
        findings.append("policy %s: Principal * with no Condition" % sid)
    return findings


def check_acl(doc):
    """Return one finding per grant to AllUsers or AuthenticatedUsers."""
    if not isinstance(doc, dict):
        raise CheckError("ACL must be a JSON object")
    grants = doc.get("Grants") or []
    if not isinstance(grants, list):
        raise CheckError("Grants must be a list")
    findings = []
    for grant in grants:
        if not isinstance(grant, dict):
            raise CheckError("every Grant must be an object")
        grantee = grant.get("Grantee")
        uri = ""
        if isinstance(grantee, dict):
            uri = grantee.get("URI") or ""
        if not isinstance(uri, str):
            continue
        if uri.endswith("/AllUsers") or uri.endswith("/AuthenticatedUsers"):
            name = uri.rsplit("/", 1)[-1]
            findings.append("acl %s: %s" % (grant.get("Permission", "?"), name))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Flag public statements in an S3 bucket policy and public ACL grants.",
        epilog="Exit codes: 0 clean, 1 public access found, 2 usage or input error.")
    parser.add_argument("policy", nargs="?",
                        help="bucket policy JSON file, or - for stdin")
    parser.add_argument("--acl", metavar="FILE",
                        help="bucket ACL JSON file")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print the summary only")
    args = parser.parse_args(argv)

    if not args.policy and not args.acl:
        parser.error("give a policy file, an --acl file, or both")
    if args.policy == "-" and args.acl == "-":
        parser.error("policy and --acl cannot both read from stdin")

    try:
        findings = []
        if args.policy:
            findings += check_policy(read_json(args.policy, "policy"))
        if args.acl:
            findings += check_acl(read_json(args.acl, "ACL"))
    except CheckError as exc:
        print("ERR %s" % exc, file=sys.stderr)
        return 2

    if findings:
        if not args.quiet:
            for finding in findings:
                print("PUBLIC " + finding)
        plural = "" if len(findings) == 1 else "s"
        print("PUBLIC %d finding%s" % (len(findings), plural))
        return 1
    print("OK no public policy statements or ACL grants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
