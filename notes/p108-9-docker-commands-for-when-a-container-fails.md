---
id: p108
title: "9 docker commands for when a container fails"
slug: 9-docker-commands-for-when-a-container-fails
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, Containers, DevOps, Linux, Troubleshooting]
source: "LinkedIn post P108 · Linux + IT series"
linkedin_date: 2027-06-06
design: terminal
---

# 9 docker commands for when a container fails

A container that exits or restarts in a loop is frustrating until you know where to look. Nine docker commands that find the cause.

## Quick reference

### What state is it in?

```bash
# -a includes stopped ones. Exited (1) = it crashed
docker ps -a --filter name=api
# the last lines usually explain the crash
docker logs --tail 50 api
# exit 137 + OOMKilled = out of memory
docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}}' api
```

### Look inside

```bash
# a shell inside the running container
docker exec -it api sh
# the config the app really sees
docker exec api env | grep DB_
# CPU and memory right now
docker stats --no-stream
```

### Network, disk and events

```bash
# who is on the same network?
docker network inspect app_net -f '{{range .Containers}}{{.Name}} {{end}}'
# disk used by images, containers and volumes
docker system df
# what happened, in order
docker events --since 10m --filter container=api
```

## Explained

### What state is it in?

- `docker ps -a --filter name=api` — -a includes stopped containers. "Exited (1)" means the app crashed with an error. "Exited (0)" means it finished normally, which is just as wrong for a service that should keep running.
- `docker logs --tail 50 api` — the last lines of output. Most crashes explain themselves here: a missing variable, a refused database connection, a bad config file.
- `docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}}' api` — exit code 137 with OOMKilled true means the container hit its memory limit and was killed.

### Look inside

- `docker exec -it api sh` — a shell inside a running container. Check files, permissions and whether the app can reach its dependencies.
- `docker exec api env | grep DB_` — the environment variables the app actually received. A typo in a compose file shows up immediately.
- `docker stats --no-stream` — CPU and memory per container right now, next to the memory limit.

### Network, disk and events

- `docker network inspect app_net` — which containers share a network. Two containers on different networks cannot reach each other by name.
- `docker system df` — disk used by images, containers, volumes and build cache, with how much can be reclaimed. A full disk stops containers from starting.
- `docker events --since 10m --filter container=api` — a timeline of what happened to the container: start, die, restart, OOM.

The order that works: status, logs, exit code. Only then rebuild or change anything.

## In one line

> **The container already told you.** Read the logs and the exit code before you rebuild anything.

**Try it**

```bash
docker logs --tail 50 api
```
