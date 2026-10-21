---
id: p528
title: "9 commands to debug a Python automation script"
slug: 9-commands-to-debug-a-python-automation-script
sections: [devsecops]
topic: "Python scripts"
tags: [Python, Debugging, DevSecOps, Linux, Automation]
source: "LinkedIn post P528 · PythonSec series"
linkedin_date: 2030-02-10
design: terminal
---

# 9 commands to debug a Python automation script

The script works on your laptop and exits 0 in cron. Nothing changed except the environment, and the traceback is not helping. Three tabs, nine commands, one question at a time.

## Quick reference

### Where did it go?

```bash
# every line, in order
python3 -m trace --trace audit.py /tmp/f
# stop before the line you doubt
python3 -m pdb audit.py /tmp/f
# dev mode turns warnings on
python3 -X dev audit.py /tmp/f
```

### Where did it spend the time?

```bash
# wall clock first, then CPU
time python3 audit.py /tmp/f
# the function, not the guess
python3 -m cProfile -s cumtime audit.py /tmp/f
# slow imports hide here
python3 -X importtime audit.py /tmp/f 2>&1 | tail -3
```

### What did it inherit?

```bash
# which file it really opened
strace -f -e trace=openat python3 audit.py /tmp/f
# no HOME, no locale, same result?
env -i PATH=/usr/bin python3 audit.py /tmp/f
# a shadow module changes everything
PYTHONPATH=/tmp python3 audit.py /tmp/f
```

## Explained

### Trace

`python3 -m trace --trace audit.py /tmp/f` prints every line as it runs, so the last line before the silence is the suspect. `python3 -m pdb audit.py /tmp/f` stops where you ask: break at the line you doubt and inspect the values. `python3 -X dev audit.py /tmp/f` turns on development warnings, including the unclosed file that only appears under load.

### Time

`time python3 audit.py /tmp/f` gives wall clock and CPU before any theory. `python3 -m cProfile -s cumtime audit.py /tmp/f` ranks functions by cumulative time, which finds the loop that reads the file twice. `python3 -X importtime audit.py /tmp/f 2>&1 | tail -3` shows the imports that cost more than the work.

### State

`strace -f -e trace=openat python3 audit.py /tmp/f` shows the openat line for the file it really opened, not the one you meant. env -i PATH=`/usr/bin python3 audit.py /tmp/f` runs with no HOME and no locale, which is close to cron. PYTHONPATH=`/tmp python3 audit.py /tmp/f` proves that a shadow module is not changing the result; both still print FINDING 3 findings.

> **The honest caveat:** strace and pdb are debugging tools, not production monitors. They slow the script and expose its arguments, so run them on a copy.

> **The lesson:** debug the call and the environment, not the story you tell about them.

## In one line

> **Trace the call, not the guess.** The bug is in one line; find the line, not the story.

**Try it**

```bash
python3 -m trace --trace audit.py /tmp/f | tail -5
```
