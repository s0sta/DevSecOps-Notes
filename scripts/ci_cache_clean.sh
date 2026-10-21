#!/usr/bin/env bash
# ci_cache_clean.sh - find old, large CI workspaces and caches, then delete
# only the ones you approve.
#
# Fixes: CI caches that ate the disk. Workspaces and dependency caches are
# created by every job and removed by none, so the runner fills up and the
# next build fails while unpacking. The script reports what is old and large
# enough to remove; dry-run is the default and --apply deletes.
#
# Usage:
#   ./ci_cache_clean.sh ROOT [DAYS] [MIN_MB] [options]
#
# Examples:
#   ./ci_cache_clean.sh /var/ci/workspaces
#   ./ci_cache_clean.sh /var/ci/workspaces 14 50
#   ./ci_cache_clean.sh /var/ci/workspaces 14 50 --apply
#   ./ci_cache_clean.sh /var/ci/caches 30 200 --name 'npm-*' --apply
#
# Arguments:
#   ROOT      directory whose immediate children are workspaces/caches
#   DAYS      minimum age in days (default 14)
#   MIN_MB    minimum size in megabytes (default 50)
#
# Options:
#   --name GLOB   only children matching this find -name pattern (default *)
#   --apply       delete the reported directories
#   -h, --help    print this help and exit 0
#
# Only direct children of ROOT are examined. A child is a candidate when its
# own mtime is older than DAYS and its size is at least MIN_MB. Paths are
# printed relative to ROOT, which the cron command names, so log lines stay
# short.
#
# Cron (weekly sweep, Sunday 04:00):
#   0 4 * * 0 /usr/local/bin/ci_cache_clean.sh /var/ci/workspaces 14 50 --apply
#
# Exit codes:
#   0  nothing to do, or every candidate was deleted
#   1  candidates were found (dry-run), or at least one delete failed
#   2  usage error or unreadable input
#
# Needs find, du and rm (GNU coreutils or BSD). IFS is set to newline and tab
# so directory names with spaces survive. Deletion is guarded: every resolved
# path must stay under ROOT, and ROOT itself is never deleted.
# By s0sta.com
set -euo pipefail
IFS=$'\n\t'

usage() {
    cat <<'EOF'
ci_cache_clean.sh - find old, large CI workspaces and caches, then delete
only the ones you approve.

Usage:
  ./ci_cache_clean.sh ROOT [DAYS] [MIN_MB] [options]

Arguments:
  ROOT      directory whose immediate children are workspaces/caches
  DAYS      minimum age in days (default 14)
  MIN_MB    minimum size in megabytes (default 50)

Options:
  --name GLOB   only children matching this find -name pattern (default *)
  --apply       delete the reported directories
  -h, --help    print this help and exit 0

Exit codes:
  0  nothing to do, or every candidate was deleted
  1  candidates were found (dry-run), or at least one delete failed
  2  usage error or unreadable input

By s0sta.com
EOF
}

root=""
days=14
min_mb=50
name="*"
apply=0
positionals=0

numeric() {
    case "$1" in
        ''|*[!0-9]*)
            return 1
            ;;
    esac
    return 0
}

need_value() {
    if [ "$#" -lt 2 ]; then
        printf 'ci_cache_clean: %s needs a value\n' "$1" >&2
        exit 2
    fi
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --name)
            need_value "$@"
            name=$2
            shift 2
            ;;
        --apply)
            apply=1
            shift
            ;;
        -*)
            printf 'ci_cache_clean: unknown option %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            case "$positionals" in
                0)
                    root=$1
                    ;;
                1)
                    days=$1
                    ;;
                2)
                    min_mb=$1
                    ;;
                *)
                    printf 'ci_cache_clean: unexpected argument %s\n' "$1" >&2
                    exit 2
                    ;;
            esac
            positionals=$((positionals + 1))
            shift
            ;;
    esac
done

if [ -z "$root" ]; then
    printf 'ci_cache_clean: ROOT is required\n' >&2
    usage >&2
    exit 2
fi

if ! numeric "$days" || [ "$days" -eq 0 ]; then
    printf 'ci_cache_clean: DAYS must be a positive number\n' >&2
    exit 2
fi

if ! numeric "$min_mb"; then
    printf 'ci_cache_clean: MIN_MB must be a number\n' >&2
    exit 2
fi

if [ ! -d "$root" ]; then
    printf 'CACHE root %s is not a directory\n' "$root" >&2
    exit 2
fi

root=$(cd "$root" && pwd -P)
if [ "$root" = "/" ]; then
    printf 'CACHE refusing to sweep /\n' >&2
    exit 2
fi

candidates=0
reclaimed=0
freed=0
failed=0

while IFS= read -r dir; do
    if [ -z "$dir" ]; then
        continue
    fi

    old=$(find "$dir" -prune -mtime +"$days" -print 2>/dev/null) || old=""
    if [ -z "$old" ]; then
        continue
    fi

    size=$(du -sm "$dir" 2>/dev/null | cut -f1) || size=""
    if ! numeric "$size"; then
        printf 'SKIP cannot size %s\n' "${dir#"$root"/}" >&2
        continue
    fi

    if [ "$size" -lt "$min_mb" ]; then
        continue
    fi

    rel=${dir#"$root"/}
    candidates=$((candidates + 1))
    reclaimed=$((reclaimed + size))

    if [ "$apply" -eq 0 ]; then
        printf 'WOULD DELETE %dM %s\n' "$size" "$rel"
        continue
    fi

    if ! abs=$(cd "$dir" && pwd -P); then
        printf 'SKIP vanished before delete: %s\n' "$rel" >&2
        failed=$((failed + 1))
        continue
    fi

    if [ "$abs" = "$root" ]; then
        printf 'SKIP refusing to delete the root itself\n' >&2
        failed=$((failed + 1))
        continue
    fi

    case "$abs" in
        "$root"/*)
            ;;
        *)
            printf 'SKIP resolved outside root: %s\n' "$rel" >&2
            failed=$((failed + 1))
            continue
            ;;
    esac

    if rm -rf "$abs"; then
        printf 'DELETED %dM %s\n' "$size" "$rel"
        freed=$((freed + size))
    else
        printf 'FAIL could not delete %s\n' "$rel" >&2
        failed=$((failed + 1))
    fi
done < <(find "$root" -mindepth 1 -maxdepth 1 -type d -name "$name" 2>/dev/null)

if [ "$candidates" -eq 0 ]; then
    printf 'CACHE clean: nothing older than %sd over %sM in %s\n' \
        "$days" "$min_mb" "$root"
    exit 0
fi

unit=dirs
if [ "$candidates" -eq 1 ]; then
    unit=dir
fi

if [ "$apply" -eq 1 ]; then
    if [ "$failed" -gt 0 ]; then
        printf 'CACHE %d %s, %dM freed, %d failed\n' \
            "$candidates" "$unit" "$freed" "$failed"
        exit 1
    fi
    printf 'CACHE %d %s, %dM freed\n' "$candidates" "$unit" "$freed"
    exit 0
fi

printf 'CACHE %d %s, %dM reclaimable\n' "$candidates" "$unit" "$reclaimed"
exit 1
