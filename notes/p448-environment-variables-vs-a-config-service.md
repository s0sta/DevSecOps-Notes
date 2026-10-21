---
id: p448
title: "Environment variables vs a config service"
slug: environment-variables-vs-a-config-service
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, Configuration, CloudNative, SecretsManagement, SRE]
source: "LinkedIn post P448 · DevOps series"
linkedin_date: 2029-08-07
design: compare
---

# Environment variables vs a config service

Every platform eventually asks whether configuration belongs in environment variables or in a config service, and the argument usually starts with a strong opinion and no example.

## Quick reference

| | **ENV VARS** | **CONFIG SVC** |
|:--|:--|:--|
| Where it lives | In the process | In a remote service |
| Change needs | A restart or redeploy | A restart or reload |
| Secrets | Easy to leak in CI logs | Scoped, audited access |
| Versioning | Git history, if at all | A version per change |
| Drift risk | Per-host overrides | One source of truth |
| Best for | Small, static settings | Many environments, audit |

**ENV VARS** (Keys in the process): Set by the shell, a manifest or CI, and inherited by every child process.

```bash
export DATABASE_URL=...
```

**CONFIG SVC** (Keys served at runtime): A managed API: versioned values, scoped per environment.

```bash
aws appconfig get-configuration
```

- Env vars → local, cheap, easy to leak.
- Config service → versioned, scoped, audited.

## Explained

### Where each one fits

Environment variables live in the process. The shell, a Kubernetes manifest or a CI job sets them, every child process inherits them, and a change means a restart or a redeploy. That is cheap and local, and it is why twelve-factor apps put config there.

A config service lives outside the process. A managed API versions values, scopes them per environment and records changes, and the app fetches them at boot or watches for updates. A change can reach a running service without a rebuild, and access is a permission rather than a file.

### The rows in the picture

Where it lives is the process versus a remote service. A change needs a restart versus a reload. Secrets are easy to leak in CI logs versus scoped and audited. Versioning is Git history, if anything, versus a version per change. Drift risk is per-host overrides versus one source of truth. Best for is small static settings versus many environments with an audit requirement. The panel at the bottom repeats the split in one line each.

> **The honest caveat:** a config service is another dependency on the boot path. Cache the last known good values and decide what happens when the service is unreachable, or a control plane outage becomes an application outage.

> **The lesson:** use environment variables for the process, and a service for what must change without a deploy.

Config is a runtime concern.
