#!/usr/bin/env bash
# deploy_gate.sh - five checks a deploy must pass before it touches a cluster.
#
# Fixes: a pipeline that deploys to whatever context the runner happened to
# load, into a namespace that does not exist, over a rollout that is already
# broken, during an open incident, or with a mutable image tag.
#
# Usage:
#   ./deploy_gate.sh CONTEXT NAMESPACE DEPLOYMENT [options]
#
# Examples:
#   ./deploy_gate.sh prod-eu api api
#   ./deploy_gate.sh prod-eu api api --expect-digest sha256:4f2c1d...
#   ./deploy_gate.sh prod-eu api api --alert-file /run/s0sta/freeze
#
# Options:
#   --alert-file PATH   block while PATH exists (default /var/run/s0sta/deploy.block)
#   --expect-digest D   require the running image to carry digest D
#   --kubeconfig PATH   pass --kubeconfig to every kubectl call
#   --timeout SECONDS   rollout status timeout (default 60)
#   -h, --help          print this help and exit 0
#
# Cron (nightly readiness probe; the gate itself belongs in CI):
#   0 3 * * * /usr/local/bin/deploy_gate.sh prod-eu api api >/var/log/deploy_gate.log 2>&1
#
# Exit codes:
#   0  every gate passed
#   1  at least one gate failed
#   2  usage error or unreadable input
#
# Needs kubectl on PATH. Read-only: it only runs config, get and rollout status.
# By s0sta.com
set -euo pipefail

usage() {
    cat <<'EOF'
deploy_gate.sh - five checks a deploy must pass before it touches a cluster.

Usage:
  ./deploy_gate.sh CONTEXT NAMESPACE DEPLOYMENT [options]

Arguments:
  CONTEXT      the kubectl context production expects, e.g. prod-eu
  NAMESPACE    the namespace the release belongs in, e.g. api
  DEPLOYMENT   the Deployment that is already running, e.g. api

Options:
  --alert-file PATH   block while PATH exists
                      (default /var/run/s0sta/deploy.block)
  --expect-digest D   require the running image to carry digest D
  --kubeconfig PATH   pass --kubeconfig to every kubectl call
  --timeout SECONDS   rollout status timeout (default 60)
  -h, --help          print this help and exit 0

Exit codes:
  0  every gate passed
  1  at least one gate failed
  2  usage error or unreadable input

By s0sta.com
EOF
}

context=""
namespace=""
deployment=""
alert_file="/var/run/s0sta/deploy.block"
expect_digest=""
kubeconfig=""
timeout=60

need_value() {
    if [ "$#" -lt 2 ]; then
        printf 'deploy_gate: %s needs a value\n' "$1" >&2
        exit 2
    fi
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --alert-file)
            need_value "$@"
            alert_file=$2
            shift 2
            ;;
        --expect-digest)
            need_value "$@"
            expect_digest=$2
            shift 2
            ;;
        --kubeconfig)
            need_value "$@"
            kubeconfig=$2
            shift 2
            ;;
        --timeout)
            need_value "$@"
            timeout=$2
            shift 2
            ;;
        -*)
            printf 'deploy_gate: unknown option %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -z "$context" ]; then
                context=$1
            elif [ -z "$namespace" ]; then
                namespace=$1
            elif [ -z "$deployment" ]; then
                deployment=$1
            else
                printf 'deploy_gate: unexpected argument %s\n' "$1" >&2
                exit 2
            fi
            shift
            ;;
    esac
done

if [ -z "$context" ] || [ -z "$namespace" ] || [ -z "$deployment" ]; then
    printf 'deploy_gate: CONTEXT, NAMESPACE and DEPLOYMENT are required\n' >&2
    usage >&2
    exit 2
fi

case "$timeout" in
    ''|*[!0-9]*)
        printf 'deploy_gate: --timeout must be a number of seconds\n' >&2
        exit 2
        ;;
esac

if ! command -v kubectl >/dev/null 2>&1; then
    printf 'deploy_gate: kubectl not found on PATH\n' >&2
    exit 2
fi

KUBECTL=(kubectl)
if [ -n "$kubeconfig" ]; then
    KUBECTL+=(--kubeconfig "$kubeconfig")
fi

passed=0
failed=0

ok() {
    passed=$((passed + 1))
    printf 'GATE ok   %s\n' "$1"
}

no() {
    failed=$((failed + 1))
    printf 'GATE FAIL %s\n' "$1"
}

# 1. The context the runner is pointed at. This is first because every later
#    check would answer for the wrong cluster.
current_context=$("${KUBECTL[@]}" config current-context 2>/dev/null) || current_context=""
if [ "$current_context" = "$context" ]; then
    ok "context $current_context"
else
    no "context ${current_context:-none}, want $context"
fi

# 2. The namespace exists.
if "${KUBECTL[@]}" get "namespace/$namespace" -o name >/dev/null 2>&1; then
    ok "namespace $namespace"
else
    no "namespace $namespace is missing"
fi

# 3. The rollout already running is healthy; never stack a release on a bad one.
if "${KUBECTL[@]}" rollout status "deployment/$deployment" -n "$namespace" \
        --timeout="${timeout}s" >/dev/null 2>&1; then
    ok "previous rollout $deployment"
else
    no "previous rollout $deployment is not healthy"
fi

# 4. The incident flag file. Incident automation creates it; the gate honours it.
if [ -e "$alert_file" ]; then
    no "alert file $alert_file exists"
else
    ok "no alert file"
fi

# 5. The image is pinned by digest, not by a tag that can be rebuilt.
image=$("${KUBECTL[@]}" get "deployment/$deployment" -n "$namespace" \
    -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null) || image=""

case "$image" in
    "")
        no "image is unreadable"
        ;;
    *@sha256:*)
        digest=${image##*@}
        if [ -n "$expect_digest" ] && [ "$digest" != "$expect_digest" ]; then
            no "digest $digest, want $expect_digest"
        else
            ok "image pinned $digest"
        fi
        ;;
    *)
        no "image $image is a mutable tag"
        ;;
esac

if [ "$failed" -eq 0 ]; then
    printf 'GATE %d of 5 passed\n' "$passed"
    exit 0
fi

printf 'GATE %d of 5 failed\n' "$failed"
exit 1
