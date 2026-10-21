---
id: p429
title: "A feature flag's life"
slug: a-feature-flags-life
sections: [devsecops]
topic: "Release & build engineering"
tags: [FeatureFlags, ReleaseEngineering, DevOps, CICD, ProgressiveDelivery]
source: "LinkedIn post P429 · DevOps series"
linkedin_date: 2029-06-24
design: timeline
---

# A feature flag's life

The first feature flag is exciting; the hundredth is technical debt with a dashboard. A flag has a life cycle, and most teams stop halfway through it.

## Quick reference

| Time | Step | What happens |
|:--|:--|:--|
| **01** | Create the flag | A boolean, off by default, with an owner and a removal date. |
| **02** | Deploy dark | Code reaches production; no user takes the new path yet. |
| **03** | 1 percent | A stable hash of the user ID picks the same cohort every time. |
| **04** | 10 percent | Only after error rate and latency hold against the control. |
| **05** | 100 percent | All traffic, and the old path is now dead code still shipped. |
| **06** | Remove the flag | Delete the flag and the old branch in one pull request. |

## Explained

### Create and deploy

The flag starts as a boolean in the flag service, off by default, with an owner and a removal date. The code ships dark: the new path exists in production, but no user reaches it. That separates the risk of shipping code from the risk of exposing it.

### Ramp

Then the percentage rises. One percent first, chosen by a stable hash of the user ID so the same users stay in the cohort. Ten percent only after error rate and latency hold against the control group. At 100 percent the flag is still doing work: the old path is dead code that still compiles, still ships and still gets tested.

### Remove

The last step is the one nobody schedules. Delete the flag and the old branch in the same pull request, and let the code default to the new behaviour. A flag left at 100 percent is not harmless; it is a permanent branch, a config dependency and a test case nobody remembers.

> **The honest caveat:** a percentage rollout on a low-traffic surface can take days to produce a signal. A percentage is not a significance test.

> **The lesson:** a feature flag is a temporary tool for separating deploy from release, not a permanent configuration system.

## In one line

> **Ship the code, release later.** A flag separates deploy from release; delete it when the release is done.

**Count the debt**

```bash
grep -rn featureFlag src/ | wc -l
```
