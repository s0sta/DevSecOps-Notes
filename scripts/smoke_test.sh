#!/usr/bin/env bash
# smoke_test.sh - assert status and body on the endpoints a release touches.
#
# Fixes: a smoke test with no teeth. A single curl for 200 on /health proves
# the process is listening, not that the release works. This script reads a
# list of url|expected_status|expected_body lines, retries with exponential
# backoff, asserts both the status code and a body marker, and exits 1 on the
# first endpoint that never gets there.
#
# Usage:
#   ./smoke_test.sh LIST [options]
#
# Examples:
#   ./smoke_test.sh checks.txt
#   ./smoke_test.sh checks.txt --attempts 4 --timeout 10 --verbose
#   ./smoke_test.sh checks.txt --delay 0        # no sleep between attempts
#
# List format, one endpoint per line:
#   https://api.example.com/healthz|200|"status":"ok"
#   https://api.example.com/v1/ping|200|pong
#   https://api.example.com/ready|204|
# Blank lines and lines starting with # are ignored. The body field is a
# fixed string (grep -F), not a regex; an empty body field asserts only the
# status.
#
# Options:
#   --attempts N     tries per endpoint (default 3)
#   --timeout S      curl max time per try, seconds (default 5)
#   --delay S        first backoff sleep in seconds, doubled per retry (default 2)
#   --verbose        print PASS lines as well as failures
#   -h, --help       print this help and exit 0
#
# Cron (every five minutes from a synthetic runner):
#   */5 * * * * /usr/local/bin/smoke_test.sh /etc/s0sta/checks.txt >/var/log/smoke.log 2>&1
#
# Exit codes:
#   0  every endpoint returned the expected status and body
#   1  at least one endpoint failed after all attempts
#   2  usage error, unreadable list, or a malformed line
#
# Needs curl on PATH. Read-only apart from a temporary body file.
# By s0sta.com
set -euo pipefail
IFS=$'\n\t'

usage() {
    cat <<'EOF'
smoke_test.sh - assert status and body on the endpoints a release touches.

Usage:
  ./smoke_test.sh LIST [options]

Arguments:
  LIST    one "url|expected_status|expected_body" line per endpoint
          (blank lines and # comments are ignored; empty body = status only)

Options:
  --attempts N     tries per endpoint (default 3)
  --timeout S      curl max time per try, seconds (default 5)
  --delay S        first backoff sleep in seconds, doubled per retry (default 2)
  --verbose        print PASS lines as well as failures
  -h, --help       print this help and exit 0

Exit codes:
  0  every endpoint returned the expected status and body
  1  at least one endpoint failed after all attempts
  2  usage error, unreadable list, or a malformed line

By s0sta.com
EOF
}

trim() {
    local s=$1
    s=${s#"${s%%[![:space:]]*}"}
    s=${s%"${s##*[![:space:]]}"}
    printf '%s' "$s"
}

numeric() {
    case "$1" in
        ''|*[!0-9]*)
            return 1
            ;;
    esac
    return 0
}

list=""
attempts=3
timeout=5
delay=2
verbose=0

need_value() {
    if [ "$#" -lt 2 ]; then
        printf 'smoke_test: %s needs a value\n' "$1" >&2
        exit 2
    fi
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --attempts)
            need_value "$@"
            attempts=$2
            shift 2
            ;;
        --timeout)
            need_value "$@"
            timeout=$2
            shift 2
            ;;
        --delay)
            need_value "$@"
            delay=$2
            shift 2
            ;;
        --verbose)
            verbose=1
            shift
            ;;
        -*)
            printf 'smoke_test: unknown option %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -z "$list" ]; then
                list=$1
            else
                printf 'smoke_test: unexpected argument %s\n' "$1" >&2
                exit 2
            fi
            shift
            ;;
    esac
done

if [ -z "$list" ]; then
    printf 'smoke_test: LIST is required\n' >&2
    usage >&2
    exit 2
fi

if [ ! -f "$list" ] || [ ! -r "$list" ]; then
    printf 'SMOKE cannot read list %s\n' "$list" >&2
    exit 2
fi

if ! numeric "$attempts" || [ "$attempts" -eq 0 ]; then
    printf 'smoke_test: --attempts must be a positive number\n' >&2
    exit 2
fi

if ! numeric "$timeout" || [ "$timeout" -eq 0 ]; then
    printf 'smoke_test: --timeout must be a positive number of seconds\n' >&2
    exit 2
fi

if ! numeric "$delay"; then
    printf 'smoke_test: --delay must be a number of seconds\n' >&2
    exit 2
fi

if ! command -v curl >/dev/null 2>&1; then
    printf 'smoke_test: curl not found on PATH\n' >&2
    exit 2
fi

body_file=$(mktemp "${TMPDIR:-/tmp}/smoke_test.XXXXXX")
trap 'rm -f "$body_file"' EXIT

total=0
failed=0
lineno=0

while IFS= read -r line || [ -n "$line" ]; do
    lineno=$((lineno + 1))

    case "$line" in
        ''|'#'*)
            continue
            ;;
    esac

    IFS='|' read -r url want_status want_body <<< "$line"
    url=$(trim "${url:-}")
    want_status=$(trim "${want_status:-}")
    want_body=$(trim "${want_body:-}")

    if [ -z "$url" ] || [ -z "$want_status" ] || ! numeric "$want_status"; then
        printf 'SMOKE malformed line %d: %s\n' "$lineno" "$line" >&2
        exit 2
    fi

    total=$((total + 1))
    ok=0
    code="000"
    try=1

    while [ "$try" -le "$attempts" ]; do
        code=$(curl -sS -o "$body_file" -w '%{http_code}' \
            --max-time "$timeout" "$url" 2>/dev/null) || code="000"
        ok=1

        if [ "$code" != "$want_status" ]; then
            ok=0
        fi

        if [ "$ok" -eq 1 ] && [ -n "$want_body" ]; then
            if ! grep -qF -e "$want_body" "$body_file"; then
                ok=0
            fi
        fi

        if [ "$ok" -eq 1 ]; then
            break
        fi

        if [ "$try" -lt "$attempts" ] && [ "$delay" -gt 0 ]; then
            nap=$((delay * (2 ** (try - 1))))
            sleep "$nap"
        fi

        try=$((try + 1))
    done

    if [ "$ok" -eq 1 ]; then
        if [ "$verbose" -eq 1 ]; then
            printf 'PASS %s %s\n' "$url" "$code"
        fi
    else
        if [ "$code" != "$want_status" ]; then
            printf 'FAIL %s %s want %s\n' "$url" "$code" "$want_status"
        else
            printf 'FAIL %s body lacks %s\n' "$url" "$want_body"
        fi
        failed=$((failed + 1))
    fi
done < "$list"

if [ "$total" -eq 0 ]; then
    printf 'SMOKE list %s has no endpoints\n' "$list" >&2
    exit 2
fi

if [ "$failed" -eq 0 ]; then
    printf 'SMOKE %d of %d passed\n' "$total" "$total"
    exit 0
fi

printf 'SMOKE %d of %d failed\n' "$failed" "$total"
exit 1
