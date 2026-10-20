---
id: p133
title: "Anatomy of a docker run command"
slug: anatomy-of-a-docker-run-command
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, Containers, DevOps, Linux, CloudComputing]
source: "LinkedIn post P133 · IT series"
linkedin_date: 2027-08-03
design: anatomy
---

# Anatomy of a docker run command

`docker` run is the command everyone copies and few read closely. Taken apart, it tells you exactly what kind of container you are about to start.

## Quick reference

```text
docker run -d --name api -p 8080:80 myapp:1.4
```

| Part | Name | What it means |
|:--|:--|:--|
| `docker` | The client | The Docker CLI, sending your command to the daemon. |
| `run` | The action | Create a new container from an image and start it. |
| `-d` | Detached | Run in the background and print the container ID. |
| `--name api` | A name | So you refer to it as api, not a random hash. |
| `-p 8080:80` | Port map | Host port 8080 forwards to container port 80. |
| `myapp:1.4` | The image | Name and tag. Pin a real tag, never latest. |

## Explained

`docker` is the client. It takes your command and sends it to the Docker daemon, which does the real work. That split is why Docker commands can target a remote host too.

run means create a new container from an image and start it. It is really two steps, create and start, in one. If the image is not on the machine, Docker pulls it first.

-d is detached mode. The container runs in the background and Docker prints its ID instead of streaming the logs. Leave it off and your terminal is attached to the container, which is handy for a quick test.

`--name api` gives the container a readable name. Without it, Docker invents a random one, and every later command has to use the ID. A clear name makes `docker` logs, `docker` exec and `docker` stop much easier.

`-p 8080:80` publishes a port. Traffic to port 8080 on the host is forwarded to port 80 inside the container. The order is host:container, and getting it backwards is a classic mistake. For safety, bind to a specific address: -p 127.0.0.1:8080:80.

`myapp:1.4` is the image and tag. The tag is the part people skip, and latest is not a version: it is whatever was newest when you pulled. Pin a real tag so the same command gives the same container next month.

## In one line

> **Read the command, know the container.** Each flag is a decision you can explain.

**See what is running**

```bash
docker ps
```
