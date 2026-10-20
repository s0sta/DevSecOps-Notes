---
id: p113
title: "5 Docker mistakes in production"
slug: 5-docker-mistakes-in-production
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, DevOps, Containers, CyberSecurity, Linux]
source: "LinkedIn post P113 · Linux + IT series"
linkedin_date: 2027-06-17
design: dontdo
---

# 5 Docker mistakes in production

Docker makes it easy to run anything. These five habits are fine on a laptop and risky on a production server.

## Quick reference

**1.** ❌ **FROM node:latest** — The next rebuild can pull a very different version.  
✅ **FROM node:22.11.0-alpine** — Pin the version. Update on purpose, not by accident.

**2. Don't**

no USER line (runs as root)

Any breakout starts with full root rights.

**Do instead**

```bash
USER app
```

Run the process as an unprivileged user.

**3. Don't**

```bash
ENV DB_PASSWORD=secret
```

Baked into the image. Anyone who pulls it can read it.

**Do instead**

```bash
docker run --env-file .env app
```

Pass secrets at runtime, or use a secrets manager.

**4. Don't**

```bash
-p 5432:5432
```

Publishes the database on every interface, past ufw.

**Do instead**

```bash
-p 127.0.0.1:5432:5432
```

Bind to localhost, or keep it on an internal network.

**5. Don't**

```bash
docker run -d app
```

After a crash or a reboot, it simply stays down.

**Do instead**

```bash
docker run -d --restart unless-stopped app
```

Comes back after crashes and host reboots.

## Explained

1. FROM node:latest
   latest is not a version, it is whatever was newest when you built. Next month's rebuild can bring a new major version and break the app without a single code change. Instead: pin an exact tag like node:22.11.0-alpine, and update it deliberately.

2. No USER line, so the app runs as root
   By default the process inside the container is root. If the app is compromised and the attacker breaks out of the container, they start with root rights. Instead: create a user in the Dockerfile and add `USER app`.

3. `ENV DB_PASSWORD=secret` in the Dockerfile
   Everything in a Dockerfile ends up in the image layers. Anyone who can pull the image can read it with docker history or docker inspect. Instead: pass secrets at runtime with `--env-file` or a secrets manager, and keep .env files out of git.

4. `-p 5432:5432`
   This publishes the port on every interface. Docker writes its own iptables rules, so the port can be reachable from the internet even when ufw says it is blocked. Instead: `-p 127.0.0.1:5432:5432`, or no published port at all and an internal Docker network between app and database.

5. `docker run -d app`, with no restart policy
   If the app crashes, or the server reboots for an update, the container stays down until someone notices. Instead: `--restart unless-stopped`, or restart: unless-stopped in compose.

None of these take more than a minute to fix, and each one has caused real outages or breaches.

## In one line

> **Containers are easy. Production is not.** Pin it, drop root, hide secrets, bind tight, restart.

**Check what is published**

```bash
docker ps --format '{{.Names}} {{.Ports}}'
```
