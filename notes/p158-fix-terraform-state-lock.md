---
id: p158
title: "Fix: Terraform state lock"
slug: fix-terraform-state-lock
sections: [devsecops]
topic: "Terraform, Ansible & IaC"
tags: [Terraform, IaC, DevOps, CloudComputing, Troubleshooting]
source: "LinkedIn post P158 · IT series"
linkedin_date: 2027-09-30
design: steps
---

# Fix: Terraform state lock

Error acquiring the state lock. Terraform is refusing to run because the state is locked, and that lock is doing its job: it stops two applies from running at once and corrupting your infrastructure's state. The fix is to understand the lock, not to smash it.

## Quick reference

### Diagnose — Who holds the lock, and why?

- **Read the Lock Info** — Who, when, and the operation. The error prints it.
- **Ask that person** — Is an apply actually running right now?
- **Check CI** — A pipeline mid-apply holds the lock too.

### Fix — Release it the right way

- **Wait if it is live** — A real apply will release the lock when it finishes.
- `terraform force-unlock <ID>` — Only when you are sure nothing is running.
- **Re-run plan** — Confirm the state is sane before applying again.

### Prevent — Fewer locks, fewer clashes

- **One apply at a time** — Serialise applies in CI, not on laptops.
- **Remote state + DynamoDB lock** — A proper backend manages locks for you.
- **Small, separate states** — Less chance two people touch the same one.

## Explained

### Diagnose

Read the Lock Info. The error prints who holds the lock, when it was created, and which operation. This tells you most of what you need.  
Ask that person. If sara's laptop holds a lock from three minutes ago, an apply may genuinely be running. Message her before doing anything.  
Check CI. A pipeline mid-apply holds the lock too. A lock with no obvious owner is often a CI job, or a previous one that crashed.

### Fix

Wait if it is live. A real, running apply releases the lock automatically when it finishes. Patience is often the whole fix.  
`terraform force-unlock <ID>`, but only when you are certain nothing is running. This happens when an apply crashed or lost network before it could release the lock. Forcing it while another apply is live can corrupt state badly.  
Re-run terraform plan afterwards to confirm the state matches reality before you apply again.

### Prevent

One apply at a time. Run applies through CI, serialised, not from several laptops.  
Use a backend with locking. Remote state in S3 with a DynamoDB lock table, or Terraform Cloud, manages locks properly.  
Keep states small and separate, so two people rarely need the same one.

The lock is protecting you. force-unlock is a last resort, used knowingly.

## In one line

> **The lock is protecting you.** Never force-unlock blindly. Two applies at once corrupt state.

**Only when sure**

```bash
terraform force-unlock <LOCK_ID>
```
