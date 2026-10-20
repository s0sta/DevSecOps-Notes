---
id: p164
title: "9 docker compose commands for daily work"
slug: 9-docker-compose-commands-for-daily-work
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, DockerCompose, DevOps, Containers, Linux]
source: "LinkedIn post P164 · IT series"
linkedin_date: 2027-10-14
design: steps
---

# 9 docker compose commands for daily work

Docker Compose runs a whole multi-container app from a single file. Nine commands cover almost all daily work, from starting the stack to looking inside it. Modern Docker uses docker compose, two words; older setups use docker-compose.

## Quick reference

### Run it — Start, stop, rebuild

```bash
# Start the whole stack in the background.
docker compose up -d
# Stop and remove it. Add -v to delete volumes too.
docker compose down
# Rebuild images, then start. After code changes.
docker compose up -d --build
```

### Look inside — What is going on?

```bash
# Which services are up, and their status and ports.
docker compose ps
# Follow one service's logs live.
docker compose logs -f api
# A shell inside a running service.
docker compose exec api sh
```

### Manage — Scale, config, clean

```bash
# Run three copies of one service.
docker compose up -d --scale worker=3
# Show the final, merged configuration.
docker compose config
# Fetch newer images before the next up.
docker compose pull
```

## Explained

### Run it

`docker compose up -d` starts every service defined in the file, in the background. App, database, cache and more come up wired together.  
`docker compose down` stops and removes the containers and network. Add -v to also delete the named volumes, which wipes the data, so use it deliberately.  
`docker compose up -d --build` rebuilds the images first. This is the one people forget after changing code, then wonder why nothing changed.

### Look inside

`docker compose ps` shows which services are running, their status, and the ports they expose.  
`docker compose logs -f api` follows one service's logs live. Leave off the name to tail everything at once.  
`docker compose exec api sh` opens a shell inside a running service, to check files, config or connectivity.

### Manage

`docker compose up -d --scale worker=3` runs three copies of a service, handy for testing a queue worker.  
`docker compose config` prints the final configuration after merging files and variables. It catches YAML and variable mistakes before they bite.  
`docker compose pull` fetches newer versions of the images before your next up.

The daily rhythm is simple: up -d to start, logs -f to watch, down to stop.

## In one line

> **One file, the whole stack.** Compose is the fastest way to run a real app locally.

**The daily two**

```bash
docker compose up -d && docker compose logs -f
```
