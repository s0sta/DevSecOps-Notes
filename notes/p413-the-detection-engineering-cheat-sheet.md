---
id: p413
title: "The detection engineering cheat sheet"
slug: the-detection-engineering-cheat-sheet
sections: [devsecops]
topic: "Incident response & detection"
tags: [DetectionEngineering, SIEM, Sigma, CyberSecurity, DevSecOps]
source: "LinkedIn post P413 · DevSecOps series"
linkedin_date: 2029-05-17
design: cheatsheet
---

# The detection engineering cheat sheet

A detection engineer's day is four kinds of command: find the log, query it, write the rule, prove it fires. Twenty commands, five per block.

## Quick reference

### Logs

```bash
tail -f /var/log/auth.log
journalctl -u sshd --since -1h
grep -c 'Failed password' auth.log
jq '.Records[] | .eventName' trail.json
aws cloudtrail lookup-events --max-items 5
```

### Queries

```bash
index=web status=5xx | stats count by uri
search errorCode=AccessDenied
| where eventName="ConsoleLogin"
earliest=-24h index=cloudtrail
| top limit=10 sourceIPAddress
```

### Rules

```bash
sigma list rules/
sigma convert -t splunk rules/
sigma check rules/
yq '.detection.selection' rules/ssh.yml
grep -n 'level: high' rules/*.yml
```

### Testing

```bash
evtx_dump security.evtx | grep 4625
chainsaw hunt evtx/ -s sigma/
grep 'ALERT' alerts.log | wc -l
jq -e '.Records | length' trail.json
python3 -m json.tool trail.json
```

## Explained

### Logs

Start where evidence lands. `tail -f /var/log/auth.log` follows authentication live, `journalctl -u sshd --since -1h` asks systemd for the hour, and `grep -c 'Failed password'` counts the failures. For cloud events, `jq '.Records[] | .eventName' trail.json` lists what happened, and `aws cloudtrail lookup-events --max-items 5` asks the API when the local file is gone.

### Queries

A query turns events into a number. `index=web status=5xx | stats count by uri` groups errors by endpoint, search errorCode=AccessDenied finds refused calls, and | where eventName="ConsoleLogin" narrows to sign-ins. `earliest=-24h index=cloudtrail` sets the window, and | top limit=10 sourceIPAddress ranks the loudest addresses.

### Rules

A rule is code. sigma list rules/ shows what you have, sigma convert -t splunk rules/ turns one format into another, and sigma check rules/ validates the schema. `yq '.detection.selection' rules/ssh.yml` reads the matching block, and `grep -n 'level: high' rules/*.yml` finds the rules that page.

### Testing

Untested rules are guesses. evtx_dump security.evtx | grep 4625 replays failed logons, and chainsaw hunt evtx/ -s sigma/ replays the rule set. `grep 'ALERT' alerts.log | wc -l` counts what fired, `jq -e '.Records | length' trail.json` proves the fixture parses, and `python3 -m json.tool trail.json` checks it before CI does.

> **The honest caveat:** sigma check validates structure, not truth. A rule can pass every lint and still match nothing in your environment.

> **The lesson:** the command is the easy part; the window and the field are the detection.

## In one line

> **Query the log, test the rule.** A rule you have not replayed is a rule you do not know.

**Start with one event**

```bash
jq '.Records[0]' trail.json
```
