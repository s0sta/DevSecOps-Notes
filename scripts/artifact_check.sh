#!/usr/bin/env bash
# artifact_check.sh - verify a release directory against a sha256 manifest.
#
# Fixes: artifacts that did not arrive. A skipped upload step, a truncated
# download or a rebuilt file leaves the deploy server with something that is
# not what the build produced. The manifest says what should be there; this
# script proves it byte by byte before the release is allowed near a cluster.
#
# Usage:
#   ./artifact_check.sh MANIFEST [BASE]
#
# Examples:
#   ./artifact_check.sh SHA256SUMS
#   ./artifact_check.sh SHA256SUMS /srv/releases/1.4.2
#   sha256sum -c SHA256SUMS          # the same check without the summary
#
# The manifest is sha256sum output: "<64 hex>  <path>", one file per line.
# Blank lines and lines starting with # are ignored. A relative path is
# resolved against BASE, which defaults to the manifest's directory. An
# absolute path is used as written.
#
# Cron (check the release directory that is about to be deployed):
#   0 5 * * * /usr/local/bin/artifact_check.sh /srv/releases/current/SHA256SUMS
#
# Exit codes:
#   0  every file exists and matches its hash
#   1  at least one file is missing or corrupt
#   2  usage error, unreadable manifest, or a malformed manifest line
#
# Needs sha256sum (GNU coreutils) or shasum -a 256 (macOS/BSD) on PATH.
# Read-only. IFS is set to newline and tab so paths with spaces survive.
# By s0sta.com
set -euo pipefail
IFS=$'\n\t'

usage() {
    cat <<'EOF'
artifact_check.sh - verify a release directory against a sha256 manifest.

Usage:
  ./artifact_check.sh MANIFEST [BASE]

Arguments:
  MANIFEST    sha256sum output: "<64 hex>  <path>", one file per line
  BASE        directory relative paths resolve against
              (default: the manifest's directory)

Examples:
  ./artifact_check.sh SHA256SUMS
  ./artifact_check.sh SHA256SUMS /srv/releases/1.4.2

Exit codes:
  0  every file exists and matches its hash
  1  at least one file is missing or corrupt
  2  usage error, unreadable manifest, or a malformed manifest line

By s0sta.com
EOF
}

if [ "$#" -eq 0 ]; then
    usage >&2
    exit 2
fi

case "$1" in
    -h|--help)
        usage
        exit 0
        ;;
    -*)
        printf 'artifact_check: unknown option %s\n' "$1" >&2
        usage >&2
        exit 2
        ;;
esac

if [ "$#" -gt 2 ]; then
    printf 'artifact_check: too many arguments\n' >&2
    usage >&2
    exit 2
fi

manifest=$1
base=${2:-}

if [ ! -f "$manifest" ] || [ ! -r "$manifest" ]; then
    printf 'ARTIFACTS cannot read manifest %s\n' "$manifest" >&2
    exit 2
fi

if [ -z "$base" ]; then
    base=$(dirname "$manifest")
fi

if [ ! -d "$base" ]; then
    printf 'ARTIFACTS base %s is not a directory\n' "$base" >&2
    exit 2
fi

if command -v sha256sum >/dev/null 2>&1; then
    sha_of() {
        sha256sum "$1" | cut -d' ' -f1
    }
elif command -v shasum >/dev/null 2>&1; then
    sha_of() {
        shasum -a 256 "$1" | cut -d' ' -f1
    }
else
    printf 'ARTIFACTS needs sha256sum or shasum on PATH\n' >&2
    exit 2
fi

total=0
bad=0

while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
        ''|'#'*)
            continue
            ;;
    esac

    hash=${line%% *}
    rest=${line#* }
    rest=${rest# }
    file=${rest#\*}

    if [ -z "$file" ] || [ "$hash" = "$line" ]; then
        printf 'ARTIFACTS malformed manifest line: %s\n' "$line" >&2
        exit 2
    fi

    case "$hash" in
        *[!0-9a-f]*)
            printf 'ARTIFACTS malformed hash: %s\n' "$line" >&2
            exit 2
            ;;
    esac

    if [ "${#hash}" -ne 64 ]; then
        printf 'ARTIFACTS hash is not 64 hex digits: %s\n' "$line" >&2
        exit 2
    fi

    total=$((total + 1))

    path=$file
    case "$path" in
        /*) ;;
        *) path="$base/$file" ;;
    esac

    if [ ! -f "$path" ]; then
        printf 'MISSING %s\n' "$file"
        bad=$((bad + 1))
        continue
    fi

    actual=$(sha_of "$path") || {
        printf 'ARTIFACTS cannot hash %s\n' "$file" >&2
        exit 2
    }

    if [ "$actual" != "$hash" ]; then
        printf 'CORRUPT %s\n' "$file"
        bad=$((bad + 1))
    fi
done < "$manifest"

if [ "$total" -eq 0 ]; then
    printf 'ARTIFACTS manifest %s has no entries\n' "$manifest" >&2
    exit 2
fi

if [ "$bad" -eq 0 ]; then
    printf 'ARTIFACTS %d of %d verified\n' "$total" "$total"
    exit 0
fi

printf 'ARTIFACTS %d bad of %d\n' "$bad" "$total"
exit 1
