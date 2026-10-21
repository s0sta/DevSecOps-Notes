---
id: p433
title: "The Docker build cheat sheet"
slug: the-docker-build-cheat-sheet
sections: [devsecops]
topic: "Release & build engineering"
tags: [Docker, DevOps, CICD, BuildSystems, Containers]
source: "LinkedIn post P433 · DevOps series"
linkedin_date: 2029-07-03
design: cheatsheet
---

# The Docker build cheat sheet

A Docker build is a cache with a command line. These are the commands that decide what gets rebuilt and what gets reused.

## Quick reference

### Build

```bash
docker build --progress=plain .
docker build --platform linux/amd64 .
docker build --target test .
docker build --no-cache .
docker build -f Dockerfile.api .
```

### Cache

```bash
docker build --cache-from api:dev .
docker buildx build --cache-to=type=gha .
docker build --no-cache-filter=test .
docker buildx prune --filter until=24h
```

### Multi-stage

```bash
docker build --target builder .
docker build --target runtime .
docker build --build-arg VERSION=2 .
docker build --ssh default .
docker build --platform linux/arm64 .
```

### Inspect

```bash
docker buildx du
docker buildx imagetools inspect api:1.0
docker history api:1.0
docker image inspect api:1.0
docker buildx inspect --bootstrap
```

## Explained

### Build

`docker build --progress=plain .` prints one DONE line per step, and that line is the only per-step timing the build itself reports. `--platform linux/amd64` pins the target architecture. `--target` test stops at the test stage. `--no-cache` rebuilds everything when you suspect the cache, and -f Dockerfile.api names the file when a repository keeps several.

### Cache

`docker build --cache-from api:dev .` reuses an image's cache, provided that image carries inline cache metadata. `--cache-to=type=gha` writes the cache to the GitHub Actions cache. `--no-cache-filter=test` rebuilds only the test stage. `docker buildx prune --filter until=24h` stops the cache eating the disk; add `--force` in CI.

### Multi-stage

`--target` builder and `--target` runtime are how one Dockerfile serves two jobs: build in the fat stage, copy into the thin one. `--build-arg VERSION=2` passes a value. `--ssh default` gives the build a key without baking it in. `--platform linux/arm64` builds for the other architecture.

### Inspect

`docker buildx du` reports what the cache costs. `docker buildx imagetools inspect api:1.0` reads the manifest in the registry. `docker history api:1.0` shows layer sizes, `docker image inspect api:1.0` shows the config, and `docker buildx inspect --bootstrap` proves which builder you are actually using.

> **The honest caveat:** `--cache-to=type=gha` only works inside GitHub Actions, where the cache API and its token exist. Anywhere else, use a registry cache or a local directory.

> **The lesson:** the flag you forget is the one that costs an hour.

## In one line

> **Build once, reuse everywhere.** A cache you cannot inspect is a cache you cannot trust.

**Plain progress**

```bash
docker build --progress=plain .
```
