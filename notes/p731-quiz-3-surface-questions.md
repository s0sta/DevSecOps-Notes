---
id: p731
title: "Quiz: 3 surface questions"
slug: quiz-3-surface-questions
sections: [devsecops]
topic: "Vulnerability management & attack surface"
tags: [CyberSecurity, AttackSurface, ASM, DNS, Python]
source: "LinkedIn post P731 · ASM series"
linkedin_date: 2031-05-29
design: quiz
---

# Quiz: 3 surface questions

Three questions close phase one. Each one comes from a tool earlier in the phase, and each answer is the mechanism behind the tool.

## Quick reference

**Q1. Why does certificate transparency find hosts that DNS brute force misses?**

- a) It records names at issuance
- b) It resolves wildcards before DNS does
- c) Brute force uses the wrong wordlist

> **Answer:** a) It records names at issuance. A cert is issued for a name before, or without, a public A record, so CT keeps staging names a wordlist never guesses. It only sees names that have a cert.

**Q2. What makes a CNAME takeover possible?**

- a) The target name is unclaimed at the provider
- b) The CNAME exceeds 255 characters
- c) The zone uses DNSSEC without NSEC3

> **Answer:** a) The target name is unclaimed at the provider. The record points at a third-party name nobody claimed, and the provider lets the next person claim it. If the provider reserves the name, there is no takeover.

**Q3. Why is ownership the hard part of asset management?**

- a) Scanners cannot see most assets
- b) An owner is a person who accepts the risk
- c) CMDB exports are hard to parse

> **Answer:** b) An owner is a person who accepts the risk. Discovery is a scan and produces facts. Ownership is a commitment: a person agrees to patch, pay for or delete the asset. A tag can be added without agreement.

## Explained

### Question one

Why does certificate transparency find hosts that DNS brute force misses? A certificate is issued for a name before, or without, a public A record. CT records the name at issuance, so a staging host that never resolved is still in the log. A wordlist only finds names someone guessed; the log finds names a CA was asked to sign.

### Question two

What makes a CNAME takeover possible? The record points at a third-party name that nobody has claimed, and the provider lets the next person claim it. If the provider reserves the name, the record is stale but not takeoverable. That is why the marker matters more than the suffix: it proves the claim page is being served.

### Question three

Why is ownership the hard part? Discovery is a scan, and a scan produces facts. Ownership is a commitment, and a commitment produces a person who agrees to patch, pay for or delete the asset. A tag or a cost centre can be filled in without anyone agreeing, which is why an asset can be fully documented and still unowned.

> **The honest caveat:** no single tool in this phase proves the surface is complete. Three independent views, CT, DNS and the cloud API, give you a defensible map, not a perfect one.

> **The lesson:** the map is a set of questions, and the answers are people.

## In one line

> **Three questions, one surface.** The map is only as good as the people who answer for it.

**Check your answer**

```bash
dig +short blog.acme.com CNAME
```
