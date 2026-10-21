---
id: p376
title: "The four questions of threat modelling"
slug: the-four-questions-of-threat-modelling
sections: [devsecops]
topic: "Application & API security"
tags: [ThreatModelling, DevSecOps, AppSec, CyberSecurity, SecureSDLC]
source: "LinkedIn post P376 · DevSecOps series"
linkedin_date: 2029-02-20
design: explainer
---

# The four questions of threat modelling

A threat model that stops after "what can go wrong" is a list of fears. The four questions are a sequence, and the last one is the only proof the first three were real.

## Quick reference

### What are we building?

- A data flow diagram with every boundary
- Actors, assets and entry points named
- The assumptions written down, not implied

### What can go wrong?

- Walk STRIDE across every boundary
- Name the attacker and the asset
- Write the abuse case, not the CVE

### What do we do?

- Accept, mitigate or block, with an owner
- One control per named threat
- One test that proves the control works

### Did we do it?

- Re-read the model against the built system
- Check the tests exist and pass
- Record what changed and why

> **Note:** A model nobody revisits is a snapshot of last quarter's assumptions.

## Explained

What are we building?  
Draw the data flow, name the actors, assets and entry points, and write down the assumptions. If the diagram cannot show where trust changes, the next question has no surface to land on.

What can go wrong?  
Walk STRIDE across every boundary, name the attacker and the asset, and write the abuse case in the user's language. "An attacker reads another tenant's invoice" is a threat; "injection" is a category.

What do we do?  
Each threat gets one of three answers: accept, mitigate or block. Mitigate names the control and the test that proves it. Accept names the owner and the review date. Block names what would unblock it.

Did we do it?  
Re-read the model against the built system, check the tests exist and pass, and record what changed. This is the step that turns a document into a programme, and the one most teams skip.

> **The honest caveat:** the four questions take an afternoon, not an hour. Rushing the first one is how you get a beautiful model of the wrong system.

> **The lesson:** a threat model is a loop, not a workshop.

## In one line

> **Ask all four, or none count.** The fourth question turns a document into a programme.

**Book the review:** diary: re-read in 90 days
