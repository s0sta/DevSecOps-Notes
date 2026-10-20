---
id: p194
title: "9 docker commands for building and shipping images"
slug: 9-docker-commands-for-building-and-shipping-images
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, DevOps, Containers, CICD, CloudNative]
source: "LinkedIn post P194 · Cloud / DevSecOps series"
linkedin_date: 2027-12-23
design: terminal
---

# 9 docker commands for building and shipping images

Before Kubernetes, you need to be fluent with images: building, tagging, shipping and cleaning them up. Nine docker commands cover the whole loop.

## Quick reference

### Build and tag

```bash
# build from the Dockerfile here, with a tag
docker build -t api:1.4.2 .
# add a second name, pointing at a registry
docker tag api:1.4.2 registry.io/team/api:1.4.2
# rebuild from scratch when cache hides a change
docker build --no-cache -t api:1.4.2 .
```

### Push and pull

```bash
# authenticate to a private registry
docker login registry.io
# upload the image
docker push registry.io/team/api:1.4.2
# fetch it on the server
docker pull registry.io/team/api:1.4.2
```

### See inside, free space

```bash
# every layer and its size. Find the fat one
docker history api:1.4.2
# the exact digest, for pinning
docker image inspect api:1.4.2 --format '{{.Id}}'
# delete unused images. Reclaim the disk
docker image prune -a
```

## Explained

### Build and tag

`docker build -t api:1.4.2 .` builds from the Dockerfile in the current directory and gives the image a name and tag. Always tag with a real version, never leave it as latest.  
`docker tag api:1.4.2 registry.io/team/api:1.4.2` adds a second name pointing at your registry. The same image can carry several tags.  
`docker build --no-cache` forces a clean rebuild when a cached layer is hiding a change, like an apt package that updated upstream.

### Push and pull

docker login authenticates to a private registry.  
docker push uploads the image and prints its digest, the content hash that identifies it exactly.  
docker pull fetches it on the target server.

### Inspect and clean

`docker history api:1.4.2` shows every layer and its size. This is how you find the one bloated layer to optimise.  
`docker image inspect --format '{{.Id}}'` gives the exact digest, which you use to deploy by digest instead of a movable tag.  
`docker image prune -a` deletes images nothing is using. On a busy build server, images and build cache quietly eat the disk; this reclaims gigabytes.

The two habits that matter: tag deliberately so you always know what you shipped, and prune on a schedule so the disk does not fill. docker system df shows how much space images, containers and cache are using right now.

## In one line

> **Tag on purpose. Prune on schedule.** Images pile up fast and quietly fill the disk.

**Try it**

```bash
docker image prune -a
```

**Pin what you ship**

```bash
docker build -t api:1.4.2 . && docker push ...
```
