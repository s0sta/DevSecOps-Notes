---
id: p460
title: "Quiz: 3 operations questions"
slug: quiz-3-operations-questions
sections: [devsecops]
topic: "Observability & SRE"
tags: [SRE, IncidentResponse, OnCall, DevOps, Reliability]
source: "LinkedIn post P460 · DevOps series"
linkedin_date: 2029-09-04
design: quiz
---

# Quiz: 3 operations questions

Three questions from the on-call work in this phase. Answer them before you read the explanations, then check your own rota against the answers.

## Quick reference

**Q1. Why does a page need an owner before it needs a fix?**

- a) An owner decides if it is real
- b) Every fix needs approval first
- c) Pages expire without an owner

> **Answer:** a) An owner decides if it is real. An unowned page has nobody to decide whether it is real, who acts, or whether it can wait until morning. A fix is a task; ownership is the routing.

**Q2. What does MTTA measure?**

- a) Detection to acknowledgement
- b) Detection to resolution
- c) Alert to deploy

> **Answer:** a) Detection to acknowledgement. MTTA starts when the incident is detected and stops when a human acknowledges. It measures the wait the rota controls, not the length of the fix.

**Q3. Why does a blameless postmortem still name actions?**

- a) Because actions need owners and dates
- b) Because blame improves memory
- c) Because reviews must name someone

> **Answer:** a) Because actions need owners and dates. Blameless removes blame from people, not responsibility from the system. Actions still get an owner, a date and a code change, so the review alters behaviour.

## Explained

### Question one

Why does a page need an owner before it needs a fix? Because an unowned page has nobody to decide whether it is real, who should act, and whether it can wait until morning. The fix is a task; ownership is the routing that gets the task to a person with context. A page without an owner is a notification.

### Question two

What does MTTA measure? The time from detection to acknowledgement, not from detection to resolution. It measures how long the system waited for a human to say "I have it", which is the part a rota controls directly. A fast MTTA with a slow MTTR is usually a staffing and knowledge problem; a slow MTTA is a paging problem.

### Question three

Why does a blameless postmortem still name actions? Because removing blame from people does not remove responsibility from the system. The review still assigns owners, dates and code changes. What it drops is the question of who to punish, which is the question that stops people from telling the truth.

> **The honest caveat:** these answers describe a healthy process, not a guarantee. A team can recite all three and still page the same person every night.

> **The lesson:** the question behind the question is who owns the response.

## In one line

> **Own the page, then fix it.** Three answers, one habit: route before you repair.

**Check one page:** does it name a person?
