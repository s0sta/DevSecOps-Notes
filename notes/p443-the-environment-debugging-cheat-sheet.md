---
id: p443
title: "The environment debugging cheat sheet"
slug: the-environment-debugging-cheat-sheet
sections: [devsecops]
topic: "DevOps basics"
tags: [DevOps, Troubleshooting, Kubernetes, Linux, SRE]
source: "LinkedIn post P443 · DevOps series"
linkedin_date: 2029-07-26
design: cheatsheet
---

# The environment debugging cheat sheet

The deploy is green and the app still cannot reach the database. Before you read the code, read the environment: four blocks cover almost every case.

## Quick reference

### DNS

```bash
dig api.staging.example.com +short
dig +trace api.example.com
cat /etc/resolv.conf
getent hosts api.staging
nslookup api.staging
```

### Ports

```bash
ss -tlnp | grep 5432
ss -tn state established
curl -sv https://api.staging/health
nc -zv db.staging 5432
kubectl get svc api -n staging
kubectl port-forward svc/api 8080:80
```

### Config

```bash
printenv | sort
env | grep -i database
kubectl exec deploy/api -- printenv
kubectl get cm api -o yaml
diff .env.staging .env.prod
python3 -m json.tool config.json
```

### Logs

```bash
kubectl logs deploy/api -f
kubectl logs deploy/api --tail=100
journalctl -u api -n 100 --no-pager
docker logs --tail 100 api
grep -i error /var/log/api.log
kubectl logs -l app=api --since=1h
```

## Explained

### DNS

Start with names. dig with +short returns the address the resolver hands back. `dig +trace` walks the delegation from the root, which shows whether the record or the resolver is wrong. `cat /etc/resolv.conf` shows which resolver the host uses, and getent hosts follows the same path as the application; dig does not read `/etc/hosts`.

### Ports

Then check the path. `ss -tlnp` lists listening TCP sockets with the process that owns them. `ss -tn state established` shows what is actually connected. `curl -sv` prints the handshake and the status line, `nc -zv` tests one port, and kubectl port-forward proves the service works before you blame the network.

### Config

Then the values. printenv dumps the process environment, env | grep narrows it, and `kubectl exec deploy/api -- printenv` reads what the container really has. kubectl get cm shows the ConfigMap behind it, diff compares two env files, and json.tool catches a broken JSON config.

### Logs

Then the story. `kubectl logs -f` follows a pod, `--tail` keeps the last hundred lines, journalctl serves systemd units, docker logs serves containers, and a grep for error finds the line. Add `--since=1h` to ignore yesterday.

> **The honest caveat:** slim images often ship without dig, ss or nc; keep a debug pod, or use kubectl debug, so the tools exist when you need them.

> **The lesson:** the environment is a hypothesis, and each block is a cheap test.

## In one line

> **The environment is a hypothesis.** Four blocks turn a guess into a check.

**Start with dns**

```bash
dig api.staging +short
```
