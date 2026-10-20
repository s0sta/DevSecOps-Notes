---
id: p109
title: "What is inside a Docker image"
slug: what-is-inside-a-docker-image
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, Containers, DevOps, CloudComputing, SoftwareEngineering]
source: "LinkedIn post P109 · Linux + IT series"
linkedin_date: 2027-06-08
design: stack
---

# What is inside a Docker image

A Docker image is not one big file. It is a stack of read-only layers, one for each step in the Dockerfile. Understanding the stack is how you get small images and fast builds.

## Quick reference

*Bottom to top: one layer per step*

1. **Base image** — OS files plus the runtime. Pin an exact version. · `FROM python:3.12-slim`
2. **System packages** — Extra libraries in one RUN, cache cleaned. · `RUN apt-get install`
3. **Dependency list** — Copied before the code so this layer is cached. · `COPY requirements.txt`
4. **Install dependencies** — Rebuilt only when the list changes. · `RUN pip install`
5. **Application code** — Changes every build. That is why it goes last. · `COPY . /app`
6. **Container layer** — Thin, writable, deleted with the container. · `docker run`

## Explained

- **L1** — Base image. FROM python:3.12-slim gives you a minimal set of OS files and the language runtime. Pin an exact version. A smaller base means fewer packages, which means fewer vulnerabilities to patch.

- **L2** — System packages. Extra libraries the app needs, installed in a single RUN step that also cleans the package cache. Split across several steps, the cache stays in the image forever.

- **L3** — Dependency list. COPY `requirements.txt` on its own, before the code. Docker reuses a cached layer when its input has not changed, so this layer is rebuilt only when the list of dependencies changes.

- **L4** — Install dependencies. RUN pip install, or npm ci, or composer install. This is usually the slowest step, and thanks to L3 it is skipped on most builds.

- **L5** — Application code. COPY . `/app`. It changes on almost every build, so it goes last. Put it earlier and every code change rebuilds everything above it.

- **L6** — Container layer. When you run the image, Docker adds a thin writable layer on top. Anything written there disappears when the container is removed, which is why databases and uploads belong in volumes.

`docker history myapp:1.0` shows every layer and its size. The biggest one is where to start optimizing.

## In one line

> **Order the layers. Builds get fast.** What changes often goes on top. Data goes in volumes.

**See the layers**

```bash
docker history myapp:1.0
```
