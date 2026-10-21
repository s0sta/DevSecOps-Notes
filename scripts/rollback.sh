#!/usr/bin/env bash
# rollback.sh - rehearse a Deployment rollback, and run it only on purpose.
#
# Fixes: the rollback nobody tested. It reads the rollout history, finds the
# revision before the current one, prints the exact kubectl rollout undo
# command and the health check to run afterwards. Dry-run is the default;
# --apply executes the undo and waits for the rollout.
#
# Usage:
#   ./rollback.sh NAMESPACE DEPLOYMENT [options]
#
# Examples:
#   ./rollback.sh api api
#   ./rollback.sh api api --to-revision 3
#   ./rollback.sh api api --apply --health-url https://api.example.com/healthz
#
# Options:
#   --to-revision N     undo to revision N instead of the previous one
#   --apply             run the undo and the health check
#   --timeout SECONDS   rollout status timeout after the undo (default 120)
#   --health-url URL    also curl this URL after the rollout is healthy
#   --kubeconfig PATH   pass --kubeconfig to every kubectl call
#   -h, --help          print this help and exit 0
#
# Cron (weekly dry-run rehearsal against staging):
#   0 4 * * 1 /usr/local/bin/rollback.sh staging api >/var/log/rollback_drill.log 2>&1
#
# Exit codes:
#   0  plan printed, or the undo ran and the rollout became healthy
#   1  no rollout history, no previous revision, or the apply failed
#   2  usage error or unreadable input
#
# Needs kubectl on PATH. curl is needed only with --health-url.
# Read-only unless --apply is passed.
# By s0sta.com
set -euo pipefail

usage() {
    cat <<'EOF'
rollback.sh - rehearse a Deployment rollback, and run it only on purpose.

Usage:
  ./rollback.sh NAMESPACE DEPLOYMENT [options]

Arguments:
  NAMESPACE    the namespace the Deployment lives in, e.g. api
  DEPLOYMENT   the Deployment to roll back, e.g. api

Options:
  --to-revision N     undo to revision N instead of the previous one
  --apply             run the undo and the health check
  --timeout SECONDS   rollout status timeout after the undo (default 120)
  --health-url URL    also curl this URL after the rollout is healthy
  --kubeconfig PATH   pass --kubeconfig to every kubectl call
  -h, --help          print this help and exit 0

Exit codes:
  0  plan printed, or the undo ran and the rollout became healthy
  1  no rollout history, no previous revision, or the apply failed
  2  usage error or unreadable input

By s0sta.com
EOF
}

namespace=""
deployment=""
to_revision=""
apply=0
timeout=120
health_url=""
kubeconfig=""

need_value() {
    if [ "$#" -lt 2 ]; then
        printf 'rollback: %s needs a value\n' "$1" >&2
        exit 2
    fi
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --to-revision)
            need_value "$@"
            to_revision=$2
            shift 2
            ;;
        --timeout)
            need_value "$@"
            timeout=$2
            shift 2
            ;;
        --health-url)
            need_value "$@"
            health_url=$2
            shift 2
            ;;
        --kubeconfig)
            need_value "$@"
            kubeconfig=$2
            shift 2
            ;;
        --apply)
            apply=1
            shift
            ;;
        -*)
            printf 'rollback: unknown option %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -z "$namespace" ]; then
                namespace=$1
            elif [ -z "$deployment" ]; then
                deployment=$1
            else
                printf 'rollback: unexpected argument %s\n' "$1" >&2
                exit 2
            fi
            shift
            ;;
    esac
done

if [ -z "$namespace" ] || [ -z "$deployment" ]; then
    printf 'rollback: NAMESPACE and DEPLOYMENT are required\n' >&2
    usage >&2
    exit 2
fi

case "$timeout" in
    ''|*[!0-9]*)
        printf 'rollback: --timeout must be a number of seconds\n' >&2
        exit 2
        ;;
esac

if [ -n "$to_revision" ]; then
    case "$to_revision" in
        ''|*[!0-9]*)
            printf 'rollback: --to-revision must be a revision number\n' >&2
            exit 2
            ;;
    esac
fi

if ! command -v kubectl >/dev/null 2>&1; then
    printf 'rollback: kubectl not found on PATH\n' >&2
    exit 2
fi

KUBECTL=(kubectl)
if [ -n "$kubeconfig" ]; then
    KUBECTL+=(--kubeconfig "$kubeconfig")
fi

history=$("${KUBECTL[@]}" rollout history "deployment/$deployment" \
    -n "$namespace" 2>/dev/null) || history=""

if [ -z "$history" ]; then
    printf 'ROLLBACK no rollout history for %s/%s\n' "$namespace" "$deployment" >&2
    exit 1
fi

revisions=$(printf '%s\n' "$history" \
    | awk 'NR > 2 && $1 ~ /^[0-9]+$/ { print $1 }' \
    | sort -n)

if [ -z "$revisions" ]; then
    printf 'ROLLBACK no numbered revisions for %s/%s\n' "$namespace" "$deployment" >&2
    exit 1
fi

current=$(printf '%s\n' "$revisions" | tail -n 1)

if [ -n "$to_revision" ]; then
    if ! printf '%s\n' "$revisions" | grep -qx -- "$to_revision"; then
        printf 'ROLLBACK revision %s is not in the history\n' "$to_revision" >&2
        exit 2
    fi
    target=$to_revision
else
    target=$(printf '%s\n' "$revisions" \
        | awk -v c="$current" '$1 + 0 < c + 0 { t = $1 } END { if (t != "") print t }')
    if [ -z "$target" ]; then
        printf 'ROLLBACK no revision before %s for %s/%s\n' \
            "$current" "$namespace" "$deployment" >&2
        exit 1
    fi
fi

if [ "$target" = "$current" ]; then
    printf 'ROLLBACK revision %s is already current\n' "$target" >&2
    exit 2
fi

kubectl_bin="kubectl"
if [ -n "$kubeconfig" ]; then
    kubectl_bin="kubectl --kubeconfig $kubeconfig"
fi

undo="$kubectl_bin rollout undo deployment/$deployment -n $namespace"
if [ -n "$to_revision" ]; then
    undo="$undo --to-revision=$target"
fi
health="$kubectl_bin rollout status deployment/$deployment -n $namespace --timeout=${timeout}s"

printf 'PLAN %s/%s revision %s -> %s\n' "$namespace" "$deployment" "$current" "$target"
printf 'UNDO %s\n' "$undo"
printf 'HEALTH %s\n' "$health"
if [ -n "$health_url" ]; then
    printf 'HEALTH curl -fsS %s\n' "$health_url"
fi

if [ "$apply" -eq 0 ]; then
    printf 'DRY-RUN nothing executed; pass --apply to run\n'
    exit 0
fi

apply_args=(rollout undo "deployment/$deployment" -n "$namespace")
if [ -n "$to_revision" ]; then
    apply_args+=(--to-revision="$target")
fi

printf 'APPLY rolling %s/%s back to revision %s\n' "$namespace" "$deployment" "$target"
if ! "${KUBECTL[@]}" "${apply_args[@]}"; then
    printf 'ROLLBACK kubectl rollout undo failed\n' >&2
    exit 1
fi

if ! "${KUBECTL[@]}" rollout status "deployment/$deployment" -n "$namespace" \
        --timeout="${timeout}s"; then
    printf 'ROLLBACK undo ran but the rollout is not healthy\n' >&2
    exit 1
fi

if [ -n "$health_url" ]; then
    if ! command -v curl >/dev/null 2>&1; then
        printf 'rollback: curl not found on PATH, needed for --health-url\n' >&2
        exit 2
    fi
    if ! curl -fsS --max-time 10 "$health_url" >/dev/null; then
        printf 'ROLLBACK rollout is healthy but %s failed\n' "$health_url" >&2
        exit 1
    fi
fi

printf 'ROLLBACK done: %s/%s at revision %s\n' "$namespace" "$deployment" "$target"
exit 0
