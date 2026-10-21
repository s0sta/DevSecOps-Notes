---
id: p522
title: "The security automation pipeline, drawn"
slug: the-security-automation-pipeline-drawn
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Python, DevSecOps, Automation, CyberSecurity, DevOps]
source: "LinkedIn post P522 · PythonSec series"
linkedin_date: 2030-01-27
design: architecture
---

# The security automation pipeline, drawn

A nightly check turns red and three people open three terminals. One is reading a command, one is staring at a log, one is editing the rule that fired. They are all inside the same pipeline, just at different tiers.

## Quick reference

- **Collect:** Command output (CMD) · Log file (LOG)
- **Parse:** JSON parser (JSON) · Regex pass (RE)
- **Decide:** Rule set (RULE) · Report (OUT)

**Request flow:** Command output → JSON parser → Rule set → Report; Log file → Regex pass → Rule set

**Around it:** Exit code (EXIT)

## Explained

### Collect

Command output is the first source: the text `sshd -T` or systemctl show prints. It is easy to capture and easy to trust too much, because a locale change can rewrite its shape. A log file is richer: timestamped lines, repeated warnings, and the evidence of what happened before the check ran.

### Parse

A JSON parser reads structured output: field names, nested values, types. It fails loudly on malformed input, which is what you want in a check. A regex pass reads the files that never had a schema: sshd_config, sudoers, cron. Anchor each pattern to a line and test it against a fixture that is allowed to be ugly.

### Decide

A rule set turns parsed facts into findings. One rule, one condition, one message. The report is the only thing a human reads, so it names the file, the line and the check. The exit code is the last tier: 0 clean, 1 finding, 2 the check itself broke. That code is what the pipeline believes.

> **The honest caveat:** a pipeline can parse its own output and still agree with a mistake. A fixture per tier is the only proof that the failure is visible.

> **The lesson:** draw the three tiers, then test each one where it breaks.

## In one line

> **Three tiers, three places to fail.** A broken audit can fail before it finds anything.

**Fail the job**

```bash
python3 audit.py || exit 1
```
