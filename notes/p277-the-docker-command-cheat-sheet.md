---
id: p277
title: "The Docker command cheat sheet"
slug: the-docker-command-cheat-sheet
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, DevOps, Containers, CheatSheet, CloudNative]
source: "LinkedIn post P277 · Visual series"
linkedin_date: 2028-07-04
design: cheatsheet
---

# The Docker command cheat sheet

You need to rebuild one container, read its logs and then delete a week of images. The commands are all in your history, somewhere between a kubectl line and a typo.

## Quick reference

### Images

```bash
docker images
docker pull nginx:1.27
docker build -t api:1.0 .
docker history api:1.0
docker inspect nginx:1.27
```

### Containers

```bash
docker ps -a
docker run -d -p 8080:80 nginx
docker logs -f --tail 100 api
docker exec -it api sh
docker stats --no-stream
```

### Compose

```bash
docker compose up -d
docker compose ps
docker compose logs -f api
docker compose config
docker compose down -v
```

### Cleanup

```bash
docker system df
docker container prune
docker image prune -a
docker volume prune -a
docker builder prune
```

## Explained

### Images

Start with images. `docker images` lists what is local, `docker pull nginx:1.27` fetches a pinned tag, and `docker build -t api:1.0 .` builds from the Dockerfile in the current directory. `docker history api:1.0` shows the layers, and `docker inspect nginx:1.27` prints the JSON behind the tag.

### Containers and Compose

`docker ps -a` shows running and stopped containers, and `docker run -d -p 8080:80 nginx` starts one in the background with a port mapped. `docker logs -f --tail 100 api` follows the last hundred lines, `docker exec -it api sh` opens a shell, and `docker stats --no-stream` gives one snapshot of CPU and memory. Compose uses the same verbs with a project: `docker compose up -d`, ps, logs -f api, config and down -v.

### Cleanup

Cleanup is where the disk comes back: `docker system df` shows what is using space, and container prune, image prune -a, volume prune -a and builder prune each target one kind of leftover.

> **The honest caveat:** prune commands delete data. `docker volume prune -a` removes named volumes that no container is using, and the database inside one will not ask twice.

> **The lesson:** five commands per area, typed from memory, beat a search engine and a guess.

## In one line

> **Five per area beats fifty.** You need the five you type weekly, not every flag in the manual.

**Check the disk**

```bash
docker system df
```
