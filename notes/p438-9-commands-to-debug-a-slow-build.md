---
id: p438
title: "9 commands to debug a slow build"
slug: 9-commands-to-debug-a-slow-build
sections: [devsecops]
topic: "Release & build engineering"
tags: [Docker, Performance, CICD, DevOps, BuildSystems]
source: "LinkedIn post P438 · DevOps series"
linkedin_date: 2029-07-15
design: terminal
---

# 9 commands to debug a slow build

The build took six minutes fifty-two. The interesting part is where those minutes went, and the answer is in nine commands.

## Quick reference

### Where did it go?

```bash
# wall clock first: CPU or waiting?
time docker build -t api:dev .
# the fattest layer is the first suspect
docker history --no-trunc api:dev
# one DONE line per step, with its duration
docker build --progress=plain . | grep -E 'DONE|CACHED'
```

### What was it doing?

```bash
# a wall of futex is waiting, not working
strace -f -c -o /tmp/b.strace make -j8
# under one CPU is a parallelism bug
perf stat -d make -j8
# throttled means the limit, not the code
cat /sys/fs/cgroup/cpu.stat
```

### What was rebuilt?

```bash
# know the size before you prune
docker buildx du
# add --force in CI; it prompts
docker buildx prune --filter until=24h
# pull the image first, or it is ignored
docker build --cache-from api:dev .
```

## Explained

### Time

The run starts with `docker build --progress=plain -t api:dev` . and finishes in 412.8s. `time docker build -t api:dev .` gives the wall clock that matters. `docker history --no-trunc api:dev` shows each layer's size, where the fat usually hides. `docker build --progress=plain . | grep -E 'DONE|CACHED'` shows which steps ran and which were reused, each with its own duration.

### Trace

`strace -f -c -o /tmp/b.strace make -j8` counts syscalls per process, and a wall of futex means waiting rather than working. `perf stat -d make -j8` reports CPUs utilised; a number near 1.0 on an eight-core box is a parallelism bug. `cat /sys/fs/cgroup/cpu.stat` shows nr_throttled, which means the limit, not the code.

### Cache

`docker buildx du` reports the cache size and what is reclaimable. `docker buildx prune --filter until=24h` clears the old entries, and `--force` stops it asking in CI. `docker build --cache-from api:dev .` reuses an image's cache, provided the image was built with inline cache metadata and pulled first.

The end card repeats `docker buildx du` with one number: 14.2GB reclaimable.

> **The honest caveat:** strace slows a build several-fold and perf needs permissions a container may not have, so use them to find the shape and then measure without them.

> **The lesson:** every slow build is waiting, working or rebuilding, and the command only tells you which.

## In one line

> **Time it, then trust it.** A build nobody measured is a build nobody can fix.

**Try it**

```bash
docker buildx du
```
