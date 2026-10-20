---
id: p147
title: "Quiz: 3 container questions"
slug: quiz-3-container-questions
sections: [devsecops]
topic: "Docker & containers"
tags: [Docker, Containers, DevOps, CloudNative, ITCareer]
source: "LinkedIn post P147 · IT series"
linkedin_date: 2027-09-05
design: quiz
---

# Quiz: 3 container questions

Three container questions that sort people who run docker run from people who understand what is happening. Try each first.

## Quick reference

**Q1. Where should a database's data live in Docker?**

- a) Inside the container
- b) In a named volume
- c) In the image

> **Answer:** b) In a named volume. Containers are disposable. A named volume keeps the data when the container is removed or replaced.

**Q2. What is the difference between an image and a container?**

- a) Nothing, they are the same
- b) An image is the template; a container is a running instance
- c) An image runs, a container stores

> **Answer:** b) An image is the template; a container is a running instance. An image is a read-only template. A container is a running instance of it, with a thin writable layer on top.

**Q3. Why avoid the latest tag in production?**

- a) It is slower
- b) It is not a fixed version; it can change under you
- c) It costs more

> **Answer:** b) It is not a fixed version; it can change under you. latest just means the newest at pull time. A rebuild can bring a different version and break things silently.

## Explained

1. Where should a database's data live in Docker?

> **Answer:** in a named volume. Containers are designed to be disposable. Anything written inside a container's own filesystem disappears when that container is removed or replaced, which happens on every update. A named volume lives outside the container's lifecycle, so the data survives. The same applies to uploads and anything else you cannot afford to lose.

2. What is the difference between an image and a container?

> **Answer:** an image is the read-only template; a container is a running instance of it. One image can start many containers, each with its own thin writable layer on top. This is why changes inside a running container do not change the image, and why those changes vanish when the container is gone. docker images lists templates; docker ps lists instances.

3. **Why avoid the latest tag in production?**

> **Answer:** because latest is not a version. It simply points to whatever was most recent when you pulled. A rebuild next month can pull a newer, different version and break your app with no code change and no obvious cause. Pin a specific tag, or better, an image digest, so the same deploy is always the same bytes.

The thread: containers are cattle, not pets. Treat them as disposable, keep state outside them, and pin what you run.

## In one line

> **Containers are simple, until they are not.** The basics prevent most production surprises.

**See image vs container**

```bash
docker images; docker ps -a
```
