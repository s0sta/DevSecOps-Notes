---
id: p563
title: "The log redaction cheat sheet"
slug: the-log-redaction-cheat-sheet
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Logging, Security, Python, DevSecOps, SRE]
source: "LinkedIn post P563 · PythonSec series"
linkedin_date: 2030-05-02
design: cheatsheet
---

# The log redaction cheat sheet

A log line with a bearer token in it is a credential, and pasting that line into a ticket publishes it. The fix is a short loop: find, redact, rotate, verify.

## Quick reference

### Find

```bash
grep -nE 'Bearer|AKIA[0-9A-Z]{16}' log
grep -nE '[0-9a-f]{32,}' log
journalctl -u api --since -1h
awk '/@/ {print NR": "$0}' log
```

### Redact

```bash
sed -E 's/Bearer [^ ]+/Bearer X/g' log
sed -E 's/[^ ]+@[^ ]+/EMAIL/g' log
sed -E 's/([0-9]+\.){3}[0-9]+/IP/g' log
sed -E 's/[0-9a-f]{32,}/HEX/g' log
```

### Rotate

```bash
logrotate -d /etc/logrotate.d/api
logrotate -f /etc/logrotate.d/api
journalctl --vacuum-time=7d
journalctl --vacuum-size=500M
```

### Verify

```bash
grep -c 'AKIA' log
grep -c '@' log
zgrep -c '@' log.1.gz
logrotate -d /etc/logrotate.d/api | head
```

## Explained

### Find

`grep -nE 'Bearer|AKIA[0-9A-Z]{16}' log` catches both shapes in one pass. `grep -nE '[0-9a-f]{32,}' log` finds long hex. `journalctl -u api --since -1h` reads the service journal directly. `awk '/@/ {print NR": "$0}' log` lists the lines with an at sign, the cheapest email lead.

### Redact

`sed -E 's/Bearer [^ ]+/Bearer X/g' log` keeps the scheme and masks the value. `sed -E 's/[^ ]+@[^ ]+/EMAIL/g' log` replaces an address. `sed -E 's/([0-9]+\.){3}[0-9]+/IP/g' log` replaces an IPv4 address. `sed -E 's/[0-9a-f]{32,}/HEX/g' log` replaces long hex.

### Rotate

`logrotate -d /etc/logrotate.d/api` checks the rule without moving a file; -f runs it now. `journalctl --vacuum-time=7d` and `--vacuum-size=500M` bound the journal, so the redacted copy is not the only copy. Rotation is the step that makes the mask matter.

### Verify

`grep -c 'AKIA' log` and `grep -c '@' log` count what remains. zgrep -c '@' log.1.gz checks the rotated archive. `logrotate -d /etc/logrotate.d/api | head` shows the rule it would apply.

> **The honest caveat:** redaction misses a secret split across lines or encoded in a blob, and masking a log does not revoke a key.

> **The lesson:** redact at the edge, rotate at the source.

## In one line

> **Find it, mask it, then rotate it.** A redacted log is only useful if the key behind it is dead.

**Check the archive:** zgrep -c '@' log.1.gz
