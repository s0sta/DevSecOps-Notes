---
id: p523
title: "The Python stdlib for DevSecOps"
slug: the-python-stdlib-for-devsecops
sections: [devsecops]
topic: "Python scripts"
tags: [Python, DevSecOps, StandardLibrary, Automation, CyberSecurity]
source: "LinkedIn post P523 · PythonSec series"
linkedin_date: 2030-01-29
design: cheatsheet
---

# The Python stdlib for DevSecOps

A script needs to read a file, run a command, open a socket and hash a value. Four blocks, no pip install, no dependency review, no supply-chain ticket. All of them ship with Python, and none of them needs a lockfile. That is one fewer artefact to scan, pin and patch.

## Quick reference

### Files

```bash
from pathlib import Path
Path(p).read_text(encoding="utf-8")
p.stat().st_mode & 0o777
sorted(p.parent.glob("*.conf"))
```

### Processes

```bash
import subprocess, shlex
shlex.split(cmd, posix=True)
subprocess.run(argv, check=True)
subprocess.run(argv, capture_output=True)
```

### Network

```bash
import socket, ssl
socket.create_connection((h, p), 5)
ssl.create_default_context()
sock.getpeercert()
```

### Crypto

```bash
import hashlib, hmac, secrets
hashlib.sha256(data).hexdigest()
hmac.compare_digest(a, b)
secrets.token_hex(32)
```

## Explained

### Files

from pathlib import Path starts it. `Path(p).read_text(encoding="utf-8")` returns the whole file as a string. `p.stat().st_mode & 0o777` gives the permission bits without parsing ls. `sorted(p.parent.glob("*.conf"))` lists the config files an audit should read.

### Processes

import subprocess, shlex. `shlex.split(cmd, posix=True)` turns a command into an argument list without a shell. `subprocess.run(argv, check=True)` raises on a non-zero exit. `subprocess.run(argv, capture_output=True)` keeps stdout and stderr apart, which is the only way to report one without the other.

### Network

import socket, ssl. `socket.create_connection((h, p), 5)` opens a TCP connection with a timeout. `ssl.create_default_context()` gives a verified TLS context. `sock.getpeercert()` returns the certificate as a dictionary of fields.

### Crypto

import hashlib, hmac, secrets. `hashlib.sha256(data).hexdigest()` prints a digest. `hmac.compare_digest(a, b)` compares without a timing leak. `secrets.token_hex(32)` makes a token that is safe to use.

> **The honest caveat:** the standard library gives you mechanism, not policy. It will read `/etc/shadow` if the process can, so permissions and scope are still your job.

> **The lesson:** the shortest dependency list is the one already on the host.

## In one line

> **Import the tool, not the framework.** The standard library is already installed on the host.

**Check one import**

```bash
python3 -c 'import ssl, hmac'
```
