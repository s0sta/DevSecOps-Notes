---
id: p199
title: "5 Dockerfile mistakes to avoid"
slug: 5-dockerfile-mistakes-to-avoid
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, Containers, DevOps, CICD, BestPractices]
source: "LinkedIn post P199 · Cloud / DevSecOps series"
linkedin_date: 2028-01-04
design: dontdo
---

# 5 Dockerfile mistakes to avoid

A working Dockerfile and a good Dockerfile are different things. Five mistakes that make images huge, slow to build or insecure, with the fix for each.

## Quick reference

**1. Don't**

COPY . . early in the file

Any code change busts the cache for every later step.

**Do instead**

```sql
COPY deps first, code last
```

Dependencies cache; only code rebuilds on a change.

**2.** ❌ **no .dockerignore** — You copy .git, node_modules and secrets into the image.  
✅ **a .dockerignore file** — Smaller, cleaner, safer images.

**3. Don't**

```bash
RUN apt-get install ... (no clean)
```

The package cache stays baked into the layer.

**Do instead**

install, then `rm -rf /var/lib/apt/lists/*`

Same step, smaller image.

**4.** ❌ **one big image for build + run** — Compilers and dev tools ship to production.  
✅ **multi-stage build** — Build in one stage, copy only the result to a slim one.

**5.** ❌ **FROM ubuntu  (full)** — Hundreds of MB and packages you never use.  
✅ **a slim or distroless base** — Less to download, patch and attack.

## Explained

1. **COPY .** . early in the file
   Docker caches layers, and a layer is invalidated when its input changes. Copy all your code near the top and every tiny code change busts the cache for everything below it, so dependencies reinstall every build. Instead: copy the dependency manifest first, install, then copy the code last. Now only the code layer rebuilds on a change.

2. No .dockerignore
   Without it, COPY . . drags .git, node_modules, local env files and build artifacts into the image, making it bigger and sometimes leaking secrets. Instead: add a .dockerignore, just like .gitignore.

3. `RUN apt-get install without cleaning`
   The downloaded package lists stay baked into that layer forever. Instead: in the same RUN, finish with `rm -rf /var/lib/apt/lists/*`. It must be the same step, because a later cleanup does not shrink an earlier layer.

4. One big image for building and running
   If you compile in the final image, the compiler, headers and dev tools all ship to production, bloating the image and widening the attack surface. Instead: a multi-stage build. Compile in a build stage, then copy only the finished artifact into a slim runtime stage.

5. A full base image
   FROM ubuntu pulls hundreds of MB and packages you never use. Instead: a -slim base, or distroless for compiled apps, so there is less to download, patch and attack.

The thread: order layers for caching, and ship only what runs.

## In one line

> **Order layers. Ship less.** A good Dockerfile is small, cached and has no build tools in it.

**Measure it**

```bash
docker history <image>  |  docker image ls
```
