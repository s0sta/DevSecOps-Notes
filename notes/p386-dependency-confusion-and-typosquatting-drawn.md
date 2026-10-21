---
id: p386
title: "Dependency confusion and typosquatting, drawn"
slug: dependency-confusion-and-typosquatting-drawn
sections: [devsecops]
topic: "Supply chain & SBOM"
tags: [SupplyChain, DevSecOps, AppSec, CyberSecurity, NPM]
source: "LinkedIn post P386 · DevSecOps series"
linkedin_date: 2029-03-15
design: explainer
---

# Dependency confusion and typosquatting, drawn

A developer installs a package with a familiar name and its postinstall script runs. Nobody chose it, and no source review would show it.

## Quick reference

### The public name

- Anyone can publish an unscoped name on npm
- The install script runs with your permissions
- One swapped letter is enough to catch a team
- Reserve your names before someone else does

### The private scope

- An internal name left unclaimed in public
- A fallback index can answer for it instead
- The attacker publishes a higher version
- Scope ownership and index pinning are the control

### The lockfile

- npm ci installs exactly the resolved URLs
- A changed hash is visible in the diff
- A new transitive entry is a review event
- Never commit a lockfile you did not read

### Verification

- npm audit signatures checks registry signatures
- Provenance ties a tarball to a commit and build
- Pin the registry host, not just the package name
- Test a fresh install in a clean directory

> **Note:** The attack is not a clever exploit; it is a name that resolved somewhere you did not expect.

## Explained

### The public name

Anyone can publish an unscoped name on the public registry. Attackers pick names close to popular packages: one letter swapped, a hyphen moved, a plural added. The script runs with the developer's permissions and can read environment variables, tokens and keys.

### The private scope

The second attack targets names used internally. If an internal name is unclaimed on the public registry, an attacker can claim it and publish a higher version. When the resolver falls back to the public index, or compares versions, the public copy can win. On npm the scope is the control; on pip, `--extra-index-url` creates the same fallback.

### The lockfile

The lockfile is where substitution becomes visible. npm ci installs exactly the resolved URLs and hashes in it, and a changed hash or a new host appears in the diff. A new transitive entry is a review event, not noise.

### Verification

Verification closes the loop. npm audit signatures checks the registry signatures on installed packages, provenance ties a tarball to a repository and a build, and pinning the registry host stops a fallback you did not intend. A fresh install in a clean directory proves the lockfile resolves where you think.

> **The honest caveat:** none of this stops an attacker who controls a legitimate package; it only makes the name and source visible before the install.

> **The lesson:** a package name is a claim, and the lockfile is the evidence.

## In one line

> **Claim the name, pin the source.** The attack is a name that resolved where you did not look.

**Check a name**

```bash
npm view @acme/utils version
```
